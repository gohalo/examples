import time
import logging
from typing import List, Type, TypeVar, Optional, Any

from .model import Model
from .engine import Engine
from .field import QueryExpression, JoinType, JoinClause

T = TypeVar("T", bound="Model")

logger = logging.getLogger("orm")


# 正常需要在会话开始时开启事务，退出时提交事务，不过这里暂时不支持事务
class Session(object):
    def __init__(self, engine: Engine):
        self._engine = engine
        self._reset()
        self._debug = False
        self._dryrun = False

    def _reset(self):
        self._model_class: Type[Model] | None = None
        self._where_conditions = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._join_clauses: List[JoinClause] = []

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        pass

    def debug(self, debug=True) -> "Session":
        self._debug = debug
        return self

    def dryrun(self, dryrun=True) -> "Session":
        self._debug = dryrun
        self._dryrun = dryrun
        return self

    def query(self, model_class: Type[T]) -> "Session":
        self._reset()
        self._model_class = model_class
        return self

    def filter(self, *expr: QueryExpression) -> "Session":
        self._where_conditions.extend(expr)
        return self

    def order_by(self, *fields: str) -> "Session":
        self._order_by.extend(fields)
        return self

    def limit(self, count: int) -> "Session":
        self._limit_value = count
        return self

    def offset(self, count: int) -> "Session":
        self._offset_value = count
        return self

    def join(self, model: Type[T], on_condition: str, join_type: JoinType = JoinType.INNER) -> "Session":
        """Add a JOIN clause to the query.

        Args:
            model: The model class to join with
            on_condition: The ON condition for the join (e.g., "users.id = orders.user_id")
            join_type: Type of join (INNER, LEFT, or RIGHT). Defaults to INNER JOIN.

        Returns:
            Self for method chaining

        Example:
            session.query(User).join(Order, "users.id = orders.user_id").all()
            session.query(User).join(Order, "users.id = orders.user_id", JoinType.LEFT).all()
        """
        self._join_clauses.append(JoinClause(join_type, model, on_condition))
        return self

    def _build_query(self, kwargs) -> str:
        assert self._model_class is not None
        sql = getattr(self._model_class, "__sql__", None)
        if sql is not None:
            return sql if kwargs is None else sql.format(**kwargs)
        if self._model_class.__table__ is None:
            raise RuntimeError("either '__sql__' or '__table__' should set")

        parts = [f"SELECT * FROM {self._model_class.__table__}"]

        # Add JOIN clauses
        if self._join_clauses:
            for join_clause in self._join_clauses:
                parts.append(join_clause.to_sql())

        if self._where_conditions:
            where_clauses = []
            for expr in self._where_conditions:
                where_clauses.append(expr.to_sql())
            parts.append(f"WHERE {' AND '.join(where_clauses)}")
        if self._order_by:
            parts.append(f"ORDER BY {', '.join(self._order_by)}")
        if self._limit_value is not None:
            parts.append(f"LIMIT {self._limit_value}")
        if self._offset_value is not None:
            parts.append(f"OFFSET {self._offset_value}")
        return " ".join(parts)

    def all(self, **kwargs) -> List[Model]:
        if self._engine is None or self._model_class is None:
            raise RuntimeError("engine or model class not specified")

        start = time.time()
        sql = self._build_query(kwargs)
        if self._dryrun:
            if self._debug:
                logger.info(f"execute sql: {sql}")
            return []

        results = self._engine.fetchraw(sql)
        if results is None:  # dryrun mode
            return []
        rows = []
        for _ in range(results.num_rows()):
            row = results.fetch_row(how=1)[0]
            rows.append(self._model_class(**row))
        if self._debug:
            logger.info(f"execute sql({(time.time() - start) * 1000:.2f}ms): {sql}")
        return rows

    def exec(self, sql: str) -> List[Any] | None:
        if self._engine is None:
            raise RuntimeError("engine not specified")
        return self._engine.fetchall(sql)

    def first(self, **kwargs) -> Optional[Model]:
        self._limit_value = 1
        results = self.all(**kwargs)
        return results[0] if results else None

    def count(self) -> int:
        if self._engine is None or self._model_class is None:
            raise RuntimeError("engine or model class not specified")
        if self._model_class.__table__ is None:
            raise RuntimeError("'__table__' should set")
        parts = [f"SELECT COUNT(*) as count FROM {self._model_class.__table__}"]
        if self._where_conditions:
            where_clauses = []
            for expr in self._where_conditions:
                where_clauses.append(expr.to_sql())
            parts.append(f"WHERE {' AND '.join(where_clauses)}")
        result = self._engine.fetchone(" ".join(parts))
        return int(result[0])

    def exists(self) -> bool:
        return self.count() > 0
