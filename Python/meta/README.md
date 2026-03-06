基本示例可以查看 `main.py` 使用，其中列名可以通过 `StringField("QUERY_ID", 256)` 类似方式指定，如果不指定则是列名为字段名。

表名默认是类名的小写，也可以通过 `__table__` 指定，执行查询会通过 `__init__()` 函数初始化对象，所以，在自定义 `__init__()` 函数中一定确保父类调用。

```
class ActiveQuery(Model):
    def __init__(self, **kwargs):
        self.tablets: Dict[str, Tabletx] = {}
        super().__init__(**kwargs)
```

除了常规的表映射，还可以通过 SQL 指定获取该对象的命令，而非表。

``` python
class Frontend(Model):
    __sql__ = "SHOW FRONTENDS"
    Name = StringField()
    Host = StringField()
    Version = StringField()

    def __repr__(self):
        return f"Frontend({self.Host})"

ses.query(Frontend).all()
```

如果 `__sql__` 带参数，也就是类似 `SHOW PARTITIONS FROM {schema}.{table}` 这种方式，那么就需要通过 `all(schema="test", table="foobar")` 方式调用。
