"""
Tests for Session class and query building.
"""
import pytest
from unittest.mock import Mock, call
from orm import Model, StringField, IntegerField, Session, Engine


class TestSession:
    """Test Session class."""

    def test_session_creation(self, mock_engine):
        """Test session creation with engine."""
        session = Session(mock_engine)
        assert session._engine == mock_engine
        assert session.model_class is None
        assert session._where_conditions == []
        assert session._order_by == []
        assert session._limit_value is None
        assert session._offset_value is None

    def test_session_context_manager(self, mock_engine):
        """Test session as context manager."""
        with Session(mock_engine) as session:
            assert isinstance(session, Session)

    def test_session_query(self, mock_session):
        """Test query method sets model class."""
        class User(Model):
            name = StringField()

        result = mock_session.query(User)
        assert mock_session.model_class == User
        assert result is mock_session

    def test_session_reset(self, mock_session):
        """Test _reset method clears session state."""
        class User(Model):
            name = StringField()

        mock_session.query(User)
        mock_session._limit_value = 10
        mock_session._reset()

        assert mock_session.model_class is None
        assert mock_session._limit_value is None


class TestSessionFiltering:
    """Test Session filter methods."""

    def test_filter_single_condition(self, mock_session):
        """Test filter with single condition."""
        class User(Model):
            name = StringField()

        expr = User.name == "Alice"
        result = mock_session.query(User).filter(expr)

        assert len(mock_session._where_conditions) == 1
        assert mock_session._where_conditions[0] == expr
        assert result is mock_session

    def test_filter_multiple_conditions(self, mock_session):
        """Test filter with multiple conditions."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        expr1 = User.name == "Alice"
        expr2 = User.age > 18

        result = mock_session.query(User).filter(expr1, expr2)

        assert len(mock_session._where_conditions) == 2
        assert result is mock_session

    def test_filter_chaining(self, mock_session):
        """Test chaining multiple filter calls."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        expr1 = User.name == "Alice"
        expr2 = User.age > 18

        result = mock_session.query(User).filter(expr1).filter(expr2)

        assert len(mock_session._where_conditions) == 2
        assert result is mock_session


class TestSessionOrdering:
    """Test Session order_by method."""

    def test_order_by_single_field(self, mock_session):
        """Test order by single field."""
        class User(Model):
            name = StringField()

        result = mock_session.query(User).order_by("name")

        assert mock_session._order_by == ["name"]
        assert result is mock_session

    def test_order_by_multiple_fields(self, mock_session):
        """Test order by multiple fields."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        result = mock_session.query(User).order_by("age", "name")

        assert mock_session._order_by == ["age", "name"]
        assert result is mock_session

    def test_order_by_chaining(self, mock_session):
        """Test chaining order_by calls."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        result = mock_session.query(User).order_by("age").order_by("name")

        assert mock_session._order_by == ["age", "name"]
        assert result is mock_session


class TestSessionPagination:
    """Test Session limit and offset methods."""

    def test_limit(self, mock_session):
        """Test limit method."""
        class User(Model):
            name = StringField()

        result = mock_session.query(User).limit(10)

        assert mock_session._limit_value == 10
        assert result is mock_session

    def test_offset(self, mock_session):
        """Test offset method."""
        class User(Model):
            name = StringField()

        result = mock_session.query(User).offset(5)

        assert mock_session._offset_value == 5
        assert result is mock_session

    def test_limit_and_offset(self, mock_session):
        """Test combining limit and offset."""
        class User(Model):
            name = StringField()

        result = mock_session.query(User).limit(10).offset(5)

        assert mock_session._limit_value == 10
        assert mock_session._offset_value == 5
        assert result is mock_session


class TestQueryBuilding:
    """Test SQL query building."""

    def test_build_simple_select(self, mock_session):
        """Test building simple SELECT query."""
        class User(Model):
            name = StringField()

        mock_session.query(User)
        sql = mock_session._build_query(None)

        assert sql == "SELECT * FROM user"

    def test_build_query_with_filter(self, mock_session):
        """Test building query with WHERE clause."""
        class User(Model):
            name = StringField()

        expr = User.name == "Alice"
        mock_session.query(User).filter(expr)
        sql = mock_session._build_query(None)

        assert "WHERE" in sql
        assert "name = 'Alice'" in sql

    def test_build_query_with_multiple_filters(self, mock_session):
        """Test building query with multiple WHERE conditions."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        expr1 = User.name == "Alice"
        expr2 = User.age > 18

        mock_session.query(User).filter(expr1, expr2)
        sql = mock_session._build_query(None)

        assert "WHERE" in sql
        assert "AND" in sql

    def test_build_query_with_order_by(self, mock_session):
        """Test building query with ORDER BY clause."""
        class User(Model):
            name = StringField()

        mock_session.query(User).order_by("name")
        sql = mock_session._build_query(None)

        assert "ORDER BY name" in sql

    def test_build_query_with_limit(self, mock_session):
        """Test building query with LIMIT clause."""
        class User(Model):
            name = StringField()

        mock_session.query(User).limit(10)
        sql = mock_session._build_query(None)

        assert "LIMIT 10" in sql

    def test_build_query_with_offset(self, mock_session):
        """Test building query with OFFSET clause."""
        class User(Model):
            name = StringField()

        mock_session.query(User).offset(5)
        sql = mock_session._build_query(None)

        assert "OFFSET 5" in sql

    def test_build_complex_query(self, mock_session):
        """Test building complex query with all clauses."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        expr = User.age > 18
        mock_session.query(User).filter(expr).order_by("name").limit(10).offset(5)
        sql = mock_session._build_query(None)

        assert "SELECT * FROM user" in sql
        assert "WHERE" in sql
        assert "ORDER BY" in sql
        assert "LIMIT 10" in sql
        assert "OFFSET 5" in sql

    def test_build_query_with_custom_sql(self, mock_session):
        """Test building query with __sql__ attribute."""
        class Frontend(Model):
            __sql__ = "SHOW FRONTENDS"
            Name = StringField()

        mock_session.query(Frontend)
        sql = mock_session._build_query(None)

        assert sql == "SHOW FRONTENDS"

    def test_build_query_with_parameterized_sql(self, mock_session):
        """Test building query with parameterized __sql__."""
        class Partition(Model):
            __sql__ = "SHOW PARTITIONS FROM {schema}.{table}"
            PartitionName = StringField()

        mock_session.query(Partition)
        sql = mock_session._build_query({"schema": "test", "table": "users"})

        assert sql == "SHOW PARTITIONS FROM test.users"

    def test_build_query_without_table_or_sql_raises_error(self, mock_session):
        """Test that query building fails without __table__ or __sql__."""
        class InvalidModel:
            pass

        mock_session.model_class = InvalidModel
        with pytest.raises(RuntimeError, match="either '__sql__' or '__table__' should set"):
            mock_session._build_query(None)


class TestQueryExecution:
    """Test query execution methods."""

    def test_all_returns_empty_list(self, mock_session, mock_mysql_result):
        """Test all() with no results."""
        class User(Model):
            name = StringField()

        mock_mysql_result.num_rows.return_value = 0
        results = mock_session.query(User).all()

        assert results == []

    def test_all_returns_models(self, mock_session, mock_mysql_result):
        """Test all() returns model instances."""
        class User(Model):
            name = StringField()

        mock_mysql_result.num_rows.return_value = 2
        mock_mysql_result.fetch_row.side_effect = [
            ({"name": b"Alice"},),
            ({"name": b"Bob"},),
        ]

        results = mock_session.query(User).all()

        assert len(results) == 2
        assert isinstance(results[0], User)
        assert results[0].name == "Alice"
        assert results[1].name == "Bob"

    def test_first_returns_none_when_empty(self, mock_session, mock_mysql_result):
        """Test first() returns None when no results."""
        class User(Model):
            name = StringField()

        mock_mysql_result.num_rows.return_value = 0
        result = mock_session.query(User).first()

        assert result is None

    def test_first_returns_first_model(self, mock_session, mock_mysql_result):
        """Test first() returns first model instance."""
        class User(Model):
            name = StringField()

        mock_mysql_result.num_rows.return_value = 1
        mock_mysql_result.fetch_row.return_value = ({"name": b"Alice"},)

        result = mock_session.query(User).first()

        assert isinstance(result, User)
        assert result.name == "Alice"

    def test_first_sets_limit_to_one(self, mock_session, mock_mysql_result):
        """Test first() sets limit to 1."""
        class User(Model):
            name = StringField()

        mock_mysql_result.num_rows.return_value = 0
        mock_session.query(User).first()

        assert mock_session._limit_value == 1

    def test_count_returns_count(self, mock_engine):
        """Test count() returns count value."""
        class User(Model):
            name = StringField()

        session = Session(mock_engine)
        mock_engine.fetchone = Mock(return_value=[b"42"])

        count = session.query(User).count()

        assert count == 42
        mock_engine.fetchone.assert_called_once()

    def test_count_with_filter(self, mock_engine):
        """Test count() with WHERE clause."""
        class User(Model):
            name = StringField()
            age = IntegerField()

        session = Session(mock_engine)
        mock_engine.fetchone = Mock(return_value=[b"10"])

        expr = User.age > 18
        count = session.query(User).filter(expr).count()

        assert count == 10
        call_args = mock_engine.fetchone.call_args[0][0]
        assert "WHERE" in call_args

    def test_count_without_table_raises_error(self, mock_session):
        """Test count() raises error without __table__."""
        class InvalidModel(Model):
            __sql__ = "SHOW FRONTENDS"

        mock_session.query(InvalidModel)
        with pytest.raises(RuntimeError, match="'__table__' should set for count operation"):
            mock_session.count()

    def test_exists_returns_true(self, mock_engine):
        """Test exists() returns True when count > 0."""
        class User(Model):
            name = StringField()

        session = Session(mock_engine)
        mock_engine.fetchone = Mock(return_value=[b"5"])

        result = session.query(User).exists()

        assert result is True

    def test_exists_returns_false(self, mock_engine):
        """Test exists() returns False when count = 0."""
        class User(Model):
            name = StringField()

        session = Session(mock_engine)
        mock_engine.fetchone = Mock(return_value=[b"0"])

        result = session.query(User).exists()

        assert result is False

    def test_all_without_engine_raises_error(self):
        """Test all() raises error when engine is None."""
        session = Session.__new__(Session)
        session._engine = None
        session.model_class = None

        with pytest.raises(RuntimeError, match="engine or model class not specified"):
            session.all()
