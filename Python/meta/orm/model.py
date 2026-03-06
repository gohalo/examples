import json
# from typing import List, Type

from .field import Field, StringField, IntegerField, BooleanField, JsonField


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":  # Model class is not for tables, create new object
            return super().__new__(cls, name, bases, attrs)

        fields = {}
        annotations = attrs.get("__annotations__", {})

        for k, v in attrs.items():
            if not isinstance(v, Field):
                continue
            setattr(v, "__name__", k)
            if v.__column__ is not None:
                k = v.__column__
            fields[k] = v

            # Add type annotation for the instance attribute
            # This helps type checkers understand the attribute will exist
            field_type = str
            if isinstance(v, IntegerField):
                field_type = int
            elif isinstance(v, BooleanField):
                field_type = bool
            elif isinstance(v, (StringField, JsonField)):
                field_type = str
            annotations[v.__name__] = field_type

        attrs["__table__"] = attrs.get("__table__", name.lower())
        attrs["__fields__"] = fields
        attrs["__annotations__"] = annotations
        return super().__new__(cls, name, bases, attrs)


class Model(metaclass=ModelMetaclass):
    __table__: str
    __fields__: dict

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            f = self.__fields__.get(k, None)
            if f is None:  # ignore unknown fields
                continue
            assert f.__name__ is not None

            if isinstance(f, StringField):
                v = v.decode("utf-8") if v is not None else None
            elif isinstance(f, IntegerField):
                v = int(v.decode("utf-8")) if v is not None else None
            elif isinstance(f, BooleanField):
                v = v == b"true" if v is not None else None
            elif isinstance(f, JsonField):
                v = json.loads(v.decode("utf-8")) if v is not None else None
            setattr(self, f.__name__, v)

    def __getattr__(self, name):
        # This method is called when an attribute is not found
        # It helps with type checking for dynamically set attributes
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    # def save(self) -> None:
    #         fields = []
    #         placeholders = []
    #         values = []
    #
    #         for field_name, field_obj in self.__fields__.items():
    #             if field_name == self.__primary_key__ and getattr(self, field_name) is None:
    #                 continue  # 主键为 None 时跳过（自增主键）
    #
    #             fields.append(field_name)
    #             placeholders.append("%s")
    #             values.append(getattr(self, field_name, field_obj.default))
    #
    #         if getattr(self, self.__primary_key__, None) is None:
    #             # 插入新记录
    #             sql = f"INSERT INTO {self.__table__} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
    #         else:
    #             # 更新现有记录
    #             set_clause = ", ".join(
    #                 [f"{field} = %s" for field in fields if field != self.__primary_key__]
    #             )
    #             sql = f"UPDATE {self.__table__} SET {set_clause} WHERE {self.__primary_key__} = %s"
    #             values = [
    #                 v for k, v in zip(fields, values) if k != self.__primary_key__
    #             ] + [getattr(self, self.__primary_key__)]
    #
    #         conn = self.get_connection()
    #         try:
    #             with conn.cursor() as cursor:
    #                 cursor.execute(sql, values)
    #                 # 如果是插入操作且主键是自增的，获取生成的主键
    #                 if (
    #                     getattr(self, self.__primary_key__, None) is None
    #                     and self.__fields__[self.__primary_key__].default is None
    #                 ):
    #                     self.id = cursor.lastrowid
    #             conn.commit()
    #         except Exception as e:
    #             conn.rollback()
    #             raise e
    #         finally:
    #             conn.close()
    #
    #     @classmethod
    #     def get(cls: Type[T], pk: Any) -> Optional[T]:
    #         """根据主键获取记录"""
    #         sql = f"SELECT * FROM {cls.__table__} WHERE {cls.__primary_key__} = %s"
    #         conn = cls.get_connection()
    #         try:
    #             with conn.cursor(pymysql.cursors.DictCursor) as cursor:
    #                 cursor.execute(sql, (pk,))
    #                 result = cursor.fetchone()
    #                 if result:
    #                     return cls(**result)
    #                 return None
    #         finally:
    #             conn.close()

    # @classmethod
    # def _create(cls):
    #     filtered = {}
    #     return cls(**filtered)
    #
    # @classmethod
    # def filter(cls: Type[T], *expres) -> QuerySet:
    #     return QuerySet(cls).filter(*expres)
    #
    # @classmethod
    # def all(cls, **kwargs) -> List[T]:  # type: ignore
    #     return QuerySet(cls).all(**kwargs)


#     def delete(self) -> None:
#         """删除当前记录"""
#         if getattr(self, self.__primary_key__, None) is None:
#             raise ValueError("无法删除未保存的记录")
#
#         sql = f"DELETE FROM {self.__table__} WHERE {self.__primary_key__} = %s"
#         conn = self.get_connection()
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute(sql, (getattr(self, self.__primary_key__),))
#             conn.commit()
#         except Exception as e:
#             conn.rollback()
#             raise e
#         finally:
#             conn.close()
#
#     @classmethod
#     def create_table(cls) -> None:
#         """创建数据表"""
#         fields_definitions = []
#
#         for field_name, field_obj in cls.__fields__.items():
#             definition = f"{field_name} {field_obj.field_type}"
#
#             if not field_obj.nullable:
#                 definition += " NOT NULL"
#
#             if field_obj.primary_key:
#                 definition += " PRIMARY KEY"
#                 if field_obj.field_type == "INT" and field_obj.default is None:
#                     definition += " AUTO_INCREMENT"
#
#             if field_obj.default is not None:
#                 if isinstance(field_obj.default, str):
#                     definition += f" DEFAULT '{field_obj.default}'"
#                 else:
#                     definition += f" DEFAULT {field_obj.default}"
#
#             fields_definitions.append(definition)
#
#         sql = f"CREATE TABLE IF NOT EXISTS {cls.__table__} ({', '.join(fields_definitions)})"
#
#         conn = cls.get_connection()
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute(sql)
#             conn.commit()
#         finally:
#             conn.close()
#
