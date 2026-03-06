import time
import random
import logging

from MySQLdb import OperationalError, _mysql as mysql

from .base import Engine

logger = logging.getLogger("orm")


def _stringify(v):
    if isinstance(v, int) or isinstance(v, float):
        return str(v)
    elif isinstance(v, bytes):
        return v.decode("utf-8")
    raise RuntimeError(f"unsupport type {type(v)}")


# 自动的 SQL 重试，会按照随机顺序便利 hosts 列表，整个列表会重试三次
class DorisEngine(Engine):
    def __init__(
        self,
        hosts: list[str],
        port: int = 9030,
        user: str = "root",
        password: str = "",
        database: str = "information_schema",
    ):
        self.db = None
        self.hosts = hosts.copy()
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        random.shuffle(self.hosts)
        self._debug = False
        self._dryrun = False

    def __enter__(self):
        self._ensure_connected()
        return self

    def __exit__(self, type, value, trace):
        if self.db is None:
            return
        self.db.close()
        self.db = None

    def debug(self, debug=True):
        self._debug = debug
        return self

    def dryrun(self, dryrun=True):
        self._debug = dryrun
        self._dryrun = dryrun
        return self

    def cleanup(self):
        if self.db is None:
            return
        self.db.close()
        self.db = None

    def _ensure_connected(self):
        if self.db is not None:
            return
        for idx in range(3):
            for host in self.hosts:
                try:
                    if self._debug:
                        logger.info(f"connect to '{host}' for {idx + 1} times")
                    self.cleanup()
                    self.db = mysql.connect(
                        host=host,
                        port=self.port,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        connect_timeout=10,
                    )
                    return
                except OperationalError as e:
                    self.db = None
                    # MySQLdb.OperationalError: (2003, "Can't connect to MySQL server on 'music-doris-51.gy.ntes:9030' (60)")
                    if e.args[0] in (2003, 2005):
                        logger.error(f"connect to '{host}' failed, {repr(e)}")
                    else:
                        raise
                except Exception as e:
                    self.db = None
                    logger.error(f"connect to '{host}' failed(unhandled), {repr(e)}")
            logger.info("connect to server failed, retry in 3 seconds later.")
            time.sleep(3)
        if not hasattr(self, "db") or self.db is not None:
            raise RuntimeError(f"connect to server {self.hosts} failed")

    def fetchraw(self, sql):
        if self._debug:
            logger.info(f"execute sql: {sql}")
        if self._dryrun:
            return None
        self._ensure_connected()
        assert self.db is not None
        try:
            self.db.query(sql)
            return self.db.store_result()
        except Exception as e:
            logger.error("handle '%s' failed, %s", sql, e)
            raise

    def fetchall(self, sql):
        result = self.fetchraw(sql)
        if result is None:
            return result
        rows = []
        for _ in range(result.num_rows()):
            rows.append([v.decode("utf-8") if v is not None else None for v in result.fetch_row()[0]])
        return rows

    def fetchone(self, sql):
        rows = self.fetchall(sql)
        if rows is None or len(rows) == 0:
            raise RuntimeError(f"Empty result for {sql}")
        return rows[0]

    def _do_insert(self, sql):
        if self.db is None:
            raise RuntimeError("got invalid database connection for insert")
        try:
            self.db.query(sql)
        except Exception as e:
            logger.error("handle '%s' failed, %s", sql, e)
            raise

    def insert(self, table, columns, records, batch_size=1024):
        column = ",".join(["`{}`".format(c) for c in columns])
        for i in range(0, len(records), batch_size):
            data = []
            for rec in records[i : i + batch_size]:
                data.append(",".join(["'{}'".format(_stringify(r)) for r in rec]))
            value = ",".join(["({})".format(r) for r in data])
            self._do_insert("INSERT INTO `{}`({}) VALUES{}".format(table, column, value))
