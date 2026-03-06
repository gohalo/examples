"""
Pytest fixtures and configuration for ORM tests.
"""
import pytest
from unittest.mock import Mock, MagicMock
from orm import Engine, Session


@pytest.fixture
def mock_mysql_result():
    """Mock MySQL result object."""
    result = Mock()
    result.num_rows = Mock(return_value=0)
    result.fetch_row = Mock(return_value=[()])
    return result


@pytest.fixture
def mock_mysql_connection():
    """Mock MySQL connection."""
    conn = Mock()
    conn.query = Mock()
    conn.store_result = Mock()
    conn.close = Mock()
    return conn


@pytest.fixture
def mock_engine(mock_mysql_connection, mock_mysql_result):
    """Create a mock Engine with mocked database connection."""
    engine = Engine(hosts=["test-host"], password="test")
    engine.db = mock_mysql_connection
    mock_mysql_connection.store_result.return_value = mock_mysql_result
    return engine


@pytest.fixture
def mock_session(mock_engine):
    """Create a Session with mock engine."""
    return Session(mock_engine)
