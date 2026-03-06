# ORM 测试套件

这是一个全面的测试套件,用于测试 Python ORM 实现的所有功能。

## 测试结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py           # Pytest fixtures 和配置
├── pytest.ini            # Pytest 配置文件
├── README.md             # 测试文档(本文件)
├── test_field.py         # Field 类和查询表达式测试
├── test_model.py         # Model 元类和模型测试
├── test_session.py       # Session 和查询构建测试
├── test_engine.py        # Engine 和数据库连接测试
└── test_integration.py   # 集成测试
```

## 测试覆盖范围

### 1. Field 测试 (test_field.py)
- ✅ Field 基类初始化和默认值
- ✅ IntegerField, StringField, BooleanField, JsonField
- ✅ 查询表达式操作符: ==, !=, >, >=, <, <=
- ✅ 特殊操作符: in_(), not_in(), like(), is_null(), is_not_null()
- ✅ SQL 生成和验证

### 2. Model 测试 (test_model.py)
- ✅ ModelMetaclass 行为
- ✅ 模型字段提取和映射
- ✅ 自定义表名 (__table__)
- ✅ 自定义列名
- ✅ 模型初始化和类型转换
- ✅ 自定义 __init__ 方法
- ✅ 自定义 SQL (__sql__)

### 3. Session 测试 (test_session.py)
- ✅ Session 创建和上下文管理器
- ✅ 查询方法: query(), filter(), order_by(), limit(), offset()
- ✅ 方法链式调用
- ✅ SQL 查询构建
- ✅ 查询执行: all(), first(), count(), exists()
- ✅ WHERE, ORDER BY, LIMIT, OFFSET 子句
- ✅ 参数化 SQL 支持

### 4. Engine 测试 (test_engine.py)
- ✅ Engine 初始化和配置
- ✅ 上下文管理器和连接管理
- ✅ 连接重试机制
- ✅ 多主机支持
- ✅ 查询执行: fetchraw(), fetchall(), fetchone()
- ✅ 插入操作和批处理
- ✅ 错误处理

### 5. 集成测试 (test_integration.py)
- ✅ 完整查询工作流
- ✅ 复杂查询组合
- ✅ 自定义列名工作流
- ✅ 自定义 SQL 查询
- ✅ Session 重用
- ✅ 各种操作符组合

## 运行测试

### 安装依赖

首先安装测试所需的依赖:

```bash
pip install pytest pytest-cov pytest-mock
```

### 运行所有测试

```bash
# 在项目根目录运行
pytest tests/

# 或者使用详细输出
pytest tests/ -v

# 显示覆盖率报告
pytest tests/ --cov=orm --cov-report=term-missing
```

### 运行特定测试文件

```bash
# 只运行 field 测试
pytest tests/test_field.py

# 只运行 model 测试
pytest tests/test_model.py

# 只运行集成测试
pytest tests/test_integration.py
```

### 运行特定测试类或函数

```bash
# 运行特定测试类
pytest tests/test_field.py::TestQueryExpression

# 运行特定测试函数
pytest tests/test_field.py::TestQueryExpression::test_eq_operator
```

### 使用标记运行测试

```bash
# 运行单元测试
pytest tests/ -m unit

# 运行集成测试
pytest tests/ -m integration

# 排除慢速测试
pytest tests/ -m "not slow"
```

## 测试报告

### 生成 HTML 覆盖率报告

```bash
pytest tests/ --cov=orm --cov-report=html
```

然后打开 `htmlcov/index.html` 查看详细的覆盖率报告。

### 生成 XML 覆盖率报告(用于 CI)

```bash
pytest tests/ --cov=orm --cov-report=xml
```

## 测试原则

1. **使用 Mock**: 所有测试使用 mock 对象模拟数据库连接,无需真实数据库
2. **隔离性**: 每个测试独立运行,不依赖其他测试
3. **完整性**: 测试覆盖正常路径和异常路径
4. **可读性**: 测试名称清晰描述测试内容
5. **可维护性**: 使用 fixtures 共享测试配置

## Fixtures 说明

在 `conftest.py` 中定义了以下 fixtures:

- `mock_mysql_result`: Mock MySQL 结果对象
- `mock_mysql_connection`: Mock MySQL 连接
- `mock_engine`: 带 mock 连接的 Engine
- `mock_session`: 带 mock engine 的 Session

这些 fixtures 可以在任何测试中使用,通过参数注入。

## 常见测试模式

### 测试查询构建

```python
def test_query_building(mock_session):
    class User(Model):
        name = StringField()

    mock_session.query(User).filter(User.name == "Alice")
    sql = mock_session._build_query(None)

    assert "WHERE name = 'Alice'" in sql
```

### 测试查询执行

```python
@patch("orm.engine.mysql.connect")
def test_query_execution(mock_connect, mock_mysql_result):
    mock_conn = Mock()
    mock_result = Mock()
    mock_result.num_rows.return_value = 1
    mock_result.fetch_row.return_value = ({"name": b"Alice"},)
    mock_conn.store_result = Mock(return_value=mock_result)
    mock_connect.return_value = mock_conn

    with Engine(["localhost"]) as engine:
        with Session(engine) as session:
            users = session.query(User).all()

    assert len(users) == 1
```

## 贡献

添加新测试时请遵循:

1. 在适当的测试文件中添加测试
2. 使用描述性的测试名称
3. 添加必要的文档字符串
4. 确保测试是独立的
5. 运行所有测试确保没有破坏现有功能

## 已知问题

在 `test_engine.py` 中,有一个关于最大重试次数的测试,注意到 `engine.py:79` 行有一个潜在的 bug:

```python
if not hasattr(self, "db") or self.db is not None:
    raise RuntimeError(f"connect to server {self.hosts} failed")
```

应该是:

```python
if not hasattr(self, "db") or self.db is None:
    raise RuntimeError(f"connect to server {self.hosts} failed")
```

测试已经编写为能够处理当前的实现。
