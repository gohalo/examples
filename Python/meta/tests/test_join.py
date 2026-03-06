"""
Tests for JOIN functionality in the ORM system.
"""
import pytest
from unittest.mock import Mock, patch
from orm import Model, DorisEngine, Session, StringField, IntegerField
from orm.field import JoinType


class User(Model):
    """Test model for users."""
    __table__ = "users"
    id = IntegerField()
    name = StringField()
    age = IntegerField()


class Order(Model):
    """Test model for orders."""
    __table__ = "orders"
    id = IntegerField()
    user_id = IntegerField()
    product = StringField()
    amount = IntegerField()


class Address(Model):
    """Test model for addresses."""
    __table__ = "addresses"
    id = IntegerField()
    user_id = IntegerField()
    city = StringField()
    street = StringField()


class TestBasicJoinOperations:
    """Test basic JOIN operations."""

    @patch("MySQLdb._mysql.connect")
    def test_inner_join(self, mock_connect):
        """Test INNER JOIN between two tables."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = session.query(User).join(Order, "users.id = orders.user_id").all()

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_left_join(self, mock_connect):
        """Test LEFT JOIN between two tables."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = session.query(User).join(
                    Order, "users.id = orders.user_id", JoinType.LEFT
                ).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "LEFT JOIN orders ON users.id = orders.user_id" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_right_join(self, mock_connect):
        """Test RIGHT JOIN between two tables."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = session.query(User).join(
                    Order, "users.id = orders.user_id", JoinType.RIGHT
                ).all()

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "RIGHT JOIN orders ON users.id = orders.user_id" in call_args


class TestMultipleJoins:
    """Test multiple JOIN operations in a single query."""

    @patch("MySQLdb._mysql.connect")
    def test_multiple_inner_joins(self, mock_connect):
        """Test multiple INNER JOINs in one query."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id")
                    .join(Address, "users.id = addresses.user_id")
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args
        assert "INNER JOIN addresses ON users.id = addresses.user_id" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_mixed_join_types(self, mock_connect):
        """Test mixing different JOIN types."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id", JoinType.LEFT)
                    .join(Address, "users.id = addresses.user_id", JoinType.INNER)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "LEFT JOIN orders ON users.id = orders.user_id" in call_args
        assert "INNER JOIN addresses ON users.id = addresses.user_id" in call_args


class TestJoinWithFilters:
    """Test JOIN combined with WHERE clauses."""

    @patch("MySQLdb._mysql.connect")
    def test_join_with_filter(self, mock_connect):
        """Test JOIN with WHERE clause."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id")
                    .filter(User.age > 18)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args
        assert "WHERE age > 18" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_join_with_multiple_filters(self, mock_connect):
        """Test JOIN with multiple WHERE clauses."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id")
                    .filter(User.age > 18, User.name.like("%John%"))
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args
        assert "WHERE" in call_args
        assert "age > 18" in call_args
        assert "AND" in call_args
        assert "name LIKE '%John%'" in call_args


class TestJoinWithComplexQueries:
    """Test JOIN with complex query features."""

    @patch("MySQLdb._mysql.connect")
    def test_join_with_order_by(self, mock_connect):
        """Test JOIN with ORDER BY clause."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id")
                    .order_by("users.name", "orders.amount")
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args
        assert "ORDER BY users.name, orders.amount" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_join_with_limit_offset(self, mock_connect):
        """Test JOIN with LIMIT and OFFSET."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id")
                    .limit(10)
                    .offset(5)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "INNER JOIN orders ON users.id = orders.user_id" in call_args
        assert "LIMIT 10" in call_args
        assert "OFFSET 5" in call_args

    @patch("MySQLdb._mysql.connect")
    def test_full_join_query(self, mock_connect):
        """Test JOIN with all query features combined."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                result = (
                    session.query(User)
                    .join(Order, "users.id = orders.user_id", JoinType.LEFT)
                    .join(Address, "users.id = addresses.user_id")
                    .filter(User.age > 18)
                    .order_by("users.name")
                    .limit(20)
                    .offset(10)
                    .all()
                )

        call_args = mock_conn.query.call_args[0][0]
        assert "SELECT * FROM users" in call_args
        assert "LEFT JOIN orders ON users.id = orders.user_id" in call_args
        assert "INNER JOIN addresses ON users.id = addresses.user_id" in call_args
        assert "WHERE age > 18" in call_args
        assert "ORDER BY users.name" in call_args
        assert "LIMIT 20" in call_args
        assert "OFFSET 10" in call_args


class TestJoinQueryExecution:
    """Test actual query execution with JOINs."""

    @patch("MySQLdb._mysql.connect")
    def test_join_query_returns_results(self, mock_connect):
        """Test that JOIN query properly returns results."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 2
        mock_result.fetch_row.side_effect = [
            ({"id": b"1", "name": b"Alice", "age": b"25", "user_id": b"1", "product": b"Book", "amount": b"50"},),
            ({"id": b"2", "name": b"Bob", "age": b"30", "user_id": b"2", "product": b"Pen", "amount": b"10"},),
        ]
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                users = session.query(User).join(Order, "users.id = orders.user_id").all()

        assert len(users) == 2
        assert users[0].name == "Alice"
        assert users[1].name == "Bob"

    @patch("MySQLdb._mysql.connect")
    def test_join_query_with_first(self, mock_connect):
        """Test JOIN query with first() method."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 1
        mock_result.fetch_row.return_value = (
            {"id": b"1", "name": b"Alice", "age": b"25", "user_id": b"1", "product": b"Book", "amount": b"50"},
        )
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                user = session.query(User).join(Order, "users.id = orders.user_id").first()

        assert user is not None
        assert user.name == "Alice"

        call_args = mock_conn.query.call_args[0][0]
        assert "LIMIT 1" in call_args


class TestJoinSessionReset:
    """Test that JOIN clauses are properly reset between queries."""

    @patch("MySQLdb._mysql.connect")
    def test_join_reset_between_queries(self, mock_connect):
        """Test that JOIN clauses don't persist across different queries."""
        mock_conn = Mock()
        mock_result = Mock()
        mock_result.num_rows.return_value = 0
        mock_conn.query = Mock()
        mock_conn.store_result = Mock(return_value=mock_result)
        mock_connect.return_value = mock_conn

        with DorisEngine(["localhost"]) as engine:
            with Session(engine) as session:
                # First query with JOIN
                result1 = session.query(User).join(Order, "users.id = orders.user_id").all()

                # Second query without JOIN
                result2 = session.query(User).filter(User.age > 18).all()

        # Verify both queries were executed
        assert mock_conn.query.call_count == 2

        # Verify first query has JOIN
        first_call_args = mock_conn.query.call_args_list[0][0][0]
        assert "INNER JOIN orders" in first_call_args

        # Verify second query doesn't have JOIN from first query
        second_call_args = mock_conn.query.call_args_list[1][0][0]
        assert "JOIN" not in second_call_args
        assert "WHERE age > 18" in second_call_args
