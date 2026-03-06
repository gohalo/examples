"""
Integration tests for the ORM system.
Tests complete workflows combining multiple components.
"""
import pytest
from unittest.mock import Mock, patch
from orm import Model, DorisEngine, Session, StringField, IntegerField, BooleanField


class User(Model):
    """Test model for integration tests."""
    __table__ = "users"
    name = StringField()
    age = IntegerField()
    is_active = BooleanField()


class Product(Model):
    """Test model with custom column names."""
    product_id = StringField("PRODUCT_ID", 50)
    product_name = StringField("PRODUCT_NAME", 100)
    price = IntegerField("PRICE")


class Frontend(Model):
    """Test model with custom SQL."""
    __sql__ = "SHOW FRONTENDS"
    Name = StringField()
    Host = StringField()
    Version = StringField()


class Partition(Model):
    """Test model with parameterized SQL."""
    __sql__ = "SHOW PARTITIONS FROM {schema}.{table}"
    PartitionName = StringField()
    Size = IntegerField()


class TestBasicQueryWorkflow:
    """Test basic query workflows."""

    @patch("MySQLdb._mysql.connect")
    def test_query_all_users(self, mock_connect):
        """Test querying all users from database."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 2
        mock_result.fetch_row.side_effect = [
            ({"name": b"Alice", "age": b"25", "is_active": b"true"},),
            ({"name": b"Bob", "age": b"30", "is_active": b"false"},),
        ]
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).all()

        assert len(users) == 2
        assert users[0].name == "Alice"
        assert users[0].age == 25
        assert users[0].is_active is True
        assert users[1].name == "Bob"
        assert users[1].age == 30
        assert users[1].is_active is False

    @patch("MySQLdb._mysql.connect")
    def test_query_with_filter(self, mock_connect):
        """Test querying with filter conditions."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"name": b"Alice", "age": b"25", "is_active": b"true"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).filter(User.age > 20).all()

        assert len(users) == 1
        assert users[0].name == "Alice"

        # Verify SQL was built correctly
        call_args = mock_conn.query.call_args[0][0]
        assert "WHERE" in call_args
        assert "age > 20" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_query_with_multiple_filters(self, mock_connect):
        """Test querying with multiple filter conditions."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = (
                    session.query(User)
                    .filter(User.age > 20, User.is_active == True)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "AND" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_query_with_ordering(self, mock_connect):
        """Test querying with order by."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).order_by("age", "name").all()

        call_args = mock_conn.query.call_args[0][0]
        assert "ORDER BY age, name" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_query_with_pagination(self, mock_connect):
        """Test querying with limit and offset."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).limit(10).offset(20).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "LIMIT 10" in call_args
        assert "OFFSET 20" in call_args


class TestComplexQueryWorkflow:
    """Test complex query workflows."""

    @patch("MySQLdb._mysql.connect")
    def test_full_query_chain(self, mock_connect):
        """Test complete query with all clauses."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = (
                    session.query(User)
                    .filter(User.age > 18, User.is_active == True)
                    .order_by("age")
                    .limit(10)
                    .offset(5)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "WHERE" in call_args
        assert "AND" in call_args
        assert "ORDER BY age" in call_args
        assert "LIMIT 10" in call_args
        assert "OFFSET 5" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_query_first(self, mock_connect):
        """Test querying first record."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"name": b"Alice", "age": b"25", "is_active": b"true"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                user = session.query(User).first()

        assert user is not None
        assert user.name == "Alice"

        call_args = mock_conn.query.call_args[0][0]
        assert "LIMIT 1" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_query_count(self, mock_connect):
        """Test counting records."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = ([b"42"],)
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            engine.fetchone = Mock(return_value=[b"42"])
            with Session(engine) as session:
                count = session.query(User).count()

        assert count == 42

    @patch("MySQLdb._mysql.connect")
    def test_query_exists(self, mock_connect):
        """Test checking if records exist."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = ([b"5"],)
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            engine.fetchone = Mock(return_value=[b"5"])
            with Session(engine) as session:
                exists = session.query(User).filter(User.age > 18).exists()

        assert exists is True


class TestCustomColumnNames:
    """Test models with custom column names."""

    @patch("MySQLdb._mysql.connect")
    def test_query_with_custom_columns(self, mock_connect):
        """Test querying model with custom column names."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"PRODUCT_ID": b"P001", "PRODUCT_NAME": b"Widget", "PRICE": b"99"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                products = session.query(Product).all()

        assert len(products) == 1
        assert products[0].product_id == "P001"
        assert products[0].product_name == "Widget"
        assert products[0].price == 99

    @patch("MySQLdb._mysql.connect")
    def test_filter_with_custom_columns(self, mock_connect):
        """Test filtering on custom column names."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                products = session.query(Product).filter(Product.price > 50).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "PRICE > 50" in call_args


class TestCustomSQLQueries:
    """Test models with custom SQL."""

    @patch("MySQLdb._mysql.connect")
    def test_query_with_custom_sql(self, mock_connect):
        """Test querying with __sql__ attribute."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"Name": b"FE1", "Host": b"192.168.1.1", "Version": b"1.0.0"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                frontends = session.query(Frontend).all()

        assert len(frontends) == 1
        assert frontends[0].Name == "FE1"

        call_args = mock_conn.query.call_args[0][0]
        assert call_args == "SHOW FRONTENDS"

    @patch("MySQLdb._mysql.connect")
    def test_query_with_parameterized_sql(self, mock_connect):
        """Test querying with parameterized __sql__."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"PartitionName": b"p20230101", "Size": b"1024"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                partitions = session.query(Partition).all(schema="test_db", table="test_table")

        call_args = mock_conn.query.call_args[0][0]
        assert call_args == "SHOW PARTITIONS FROM test_db.test_table"


class TestSessionReuse:
    """Test session reuse for multiple queries."""

    @patch("MySQLdb._mysql.connect")
    def test_multiple_queries_in_session(self, mock_connect):
        """Test executing multiple queries in same session."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                # First query
                users1 = session.query(User).filter(User.age > 20).all()

                # Second query (should reset previous conditions)
                users2 = session.query(User).filter(User.age < 30).all()

        # Verify both queries were executed
        assert mock_conn.query.call_count == 2

        # Verify second query doesn't include first query's conditions
        second_call_args = mock_conn.query.call_args_list[1][0][0]
        assert "age < 30" in second_call_args
        assert "age > 20" not in second_call_args


class TestOperatorCombinations:
    """Test various operator combinations."""

    @patch("MySQLdb._mysql.connect")
    def test_in_operator(self, mock_connect):
        """Test IN operator."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).filter(User.age.in_([20, 25, 30])).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "age IN (20, 25, 30)" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_like_operator(self, mock_connect):
        """Test LIKE operator."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).filter(User.name.like("%Alice%")).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "name LIKE '%Alice%'" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_is_null_operator(self, mock_connect):
        """Test IS NULL operator."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).filter(User.name.is_null()).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "name IS NULL" in call_args
