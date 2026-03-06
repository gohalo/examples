import logging

from orm import Model, DorisEngine, Session, StringField
from orm.field import IntegerField

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class Frontend(Model):
    __sql__ = "SHOW FRONTENDS"
    Name = StringField()
    Host = StringField()
    Version = StringField()

    def __repr__(self):
        return f"Frontend({self.Host})"


class ActiveQuery(Model):
    __table__ = "active_queries"
    QueryID = StringField("QUERY_ID", 256)
    QueryTimeMS = IntegerField()

    def __repr__(self):
        return f"Query({self.QueryID})"


if __name__ == "__main__":
    hosts = ["music-doris-test-1.gy.ntes", "music-doris-test-2.gy.ntes", "music-doris-test-3.gy.ntes"]
    with DorisEngine(hosts, password="music_root").debug(False).dryrun(False) as conn:
        # print(conn.fetchall("SHOW FRONTENDS"))  # run simple sql
        with Session(conn).debug() as ses:
            print(ses.exec("SHOW FRONTENDS"))  # run simple sql

            # total = ses.query(Frontend).all()
            # print([x for x in total if x.Version == "1.0.0x"])

            # print(ses.query(ActiveQuery).first())
