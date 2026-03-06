from enum import Enum
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Model


class JoinType(Enum):
    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"


class JoinClause:
    def __init__(self, join_type: JoinType, model: "type[Model]", on_condition: str):
        self.join_type = join_type
        self.model = model
        self.on_condition = on_condition

    def to_sql(self) -> str:
        table_name = self.model.__table__
        return f"{self.join_type.value} {table_name} ON {self.on_condition}"


class Operator(Enum):
    EQ = "="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    LIKE = "LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


class QueryExpression:
    def __init__(self, field: str | None, operator: Operator, value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value

    def to_sql(self) -> str:
        val = self.value
        if isinstance(self.value, str):
            val = f"'{self.value}'"

        if self.operator in (Operator.IS_NULL, Operator.IS_NOT_NULL):
            return f"{self.field} {self.operator.value}"
        elif self.operator in (Operator.IN, Operator.NOT_IN):
            if not isinstance(self.value, (list, tuple)):
                raise ValueError(f"{self.operator.value} should be list or tuple")
            if isinstance(self.value[0], (str, bytes)):
                placeholders = ", ".join([f"'{x}'" for x in self.value])
            else:
                placeholders = ", ".join([f"{x}" for x in self.value])
            return f"{self.field} {self.operator.value} ({placeholders})"
        else:
            return f"{self.field} {self.operator.value} {val}"


class Field(object):
    def __init__(self, name: str | None, ftype: str, nullable: bool = True):
        self.__name__ = None  # field name for python object
        self.__column__ = name  # column name for the table
        self.field_type = ftype
        self.nullable = nullable

    def __eq__(self, other):  # type: ignore
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.EQ, other)

    def __ne__(self, other):  # type: ignore
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.NE, other)

    def in_(self, values: List[Any]):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.IN, values)

    def __gt__(self, other):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.GT, other)

    def __ge__(self, other):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.GE, other)

    def __lt__(self, other):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.LT, other)

    def __le__(self, other):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.LE, other)

    def like(self, pattern: str):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.LIKE, pattern)

    def not_in(self, values: List[Any]):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.NOT_IN, values)

    def is_null(self):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.IS_NULL)

    def is_not_null(self):
        column_name = self.__column__ if self.__column__ is not None else self.__name__
        return QueryExpression(column_name, Operator.IS_NOT_NULL)


class IntegerField(Field):
    def __init__(self, name: str | None = None, nullable: bool = True):
        super().__init__(name, "INT", nullable)


class StringField(Field):
    def __init__(self, name: str | None = None, length: int = 255, nullable: bool = True):
        super().__init__(name, f"VARCHAR({length})", nullable)


class BooleanField(Field):
    def __init__(self, name: str | None = None, nullable: bool = True):
        super().__init__(name, "BOOLEAN", nullable)


class JsonField(Field):
    def __init__(self, name: str | None = None, nullable: bool = True):
        super().__init__(name, "JSON", nullable)
