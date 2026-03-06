"""
Tests for Model metaclass and Model class.
"""

import pytest
import json
from orm import Model, StringField, IntegerField, BooleanField, JsonField


class TestModelMetaclass:
    """Test ModelMetaclass behavior."""

    def test_model_base_class_creation(self):
        """Test that Model base class is created without modification."""
        assert Model.__name__ == "Model"
        assert not hasattr(Model, "__fields__")

    def test_model_subclass_has_table_name(self):
        """Test that subclass gets default table name."""

        class User(Model):
            pass

        assert User.__table__ == "user"

    def test_model_custom_table_name(self):
        """Test custom table name via __table__."""

        class MyModel(Model):
            __table__ = "custom_table"

        assert MyModel.__table__ == "custom_table"

    def test_model_fields_extraction(self):
        """Test that fields are properly extracted."""

        class User(Model):
            name = StringField()
            age = IntegerField()

        assert "name" in User.__fields__
        assert "age" in User.__fields__
        assert User.name.__name__ == "name"
        assert User.age.__name__ == "age"

    def test_model_field_with_column_name(self):
        """Test field with custom column name."""

        class Query(Model):
            query_id = StringField("QUERY_ID", 256)

        assert "QUERY_ID" in Query.__fields__
        assert Query.query_id.__column__ == "QUERY_ID"
        assert Query.query_id.__name__ == "query_id"

    def test_model_non_field_attributes_ignored(self):
        """Test that non-Field attributes are ignored."""

        class User(Model):
            name = StringField()
            some_method = lambda self: "test"
            some_value = 42

        assert "name" in User.__fields__
        assert "some_method" not in User.__fields__
        assert "some_value" not in User.__fields__


class TestModelInitialization:
    """Test Model instance initialization."""

    def test_model_init_with_string_field(self):
        """Test model initialization with StringField."""

        class User(Model):
            name = StringField()

        user = User(name=b"John Doe")
        assert user.name == "John Doe"

    def test_model_init_with_integer_field(self):
        """Test model initialization with IntegerField."""

        class User(Model):
            age = IntegerField()

        user = User(age=b"25")
        assert user.age == 25

    def test_model_init_with_boolean_field_true(self):
        """Test model initialization with BooleanField (true)."""

        class User(Model):
            is_active = BooleanField()

        user = User(is_active=b"true")
        assert user.is_active is True

    def test_model_init_with_boolean_field_false(self):
        """Test model initialization with BooleanField (false)."""

        class User(Model):
            is_active = BooleanField()

        user = User(is_active=b"false")
        assert user.is_active is False

    def test_model_init_with_json_field(self):
        """Test model initialization with JsonField."""

        class User(Model):
            metadata = JsonField()

        json_data = {"key": "value", "count": 42}
        user = User(metadata=json.dumps(json_data).encode("utf-8"))
        assert user.metadata == json_data

    def test_model_init_ignores_unknown_fields(self):
        """Test that unknown fields are ignored during initialization."""

        class User(Model):
            name = StringField()

        user = User(name=b"John", unknown_field=b"value")
        assert user.name == "John"
        assert not hasattr(user, "unknown_field")

    def test_model_init_with_custom_column_name(self):
        """Test initialization with custom column name."""

        class Query(Model):
            query_id = StringField("QUERY_ID", 256)

        query = Query(QUERY_ID=b"abc123")
        assert query.query_id == "abc123"

    def test_model_with_custom_init(self):
        """Test model with custom __init__ that calls super().__init__."""

        class CustomModel(Model):
            name = StringField()

            def __init__(self, **kwargs):
                self.custom_attr = "custom"
                super().__init__(**kwargs)

        instance = CustomModel(name=b"test")
        assert instance.name == "test"
        assert instance.custom_attr == "custom"


class TestModelRepresentation:
    """Test model __repr__ and string representation."""

    def test_custom_repr(self):
        """Test custom __repr__ method."""

        class User(Model):
            name = StringField()

            def __repr__(self):
                return f"User({self.name})"

        user = User(name=b"Alice")
        assert repr(user) == "User(Alice)"


class TestModelWithSQL:
    """Test model with __sql__ attribute."""

    def test_model_with_sql_attribute(self):
        """Test that model can have __sql__ attribute."""

        class Frontend(Model):
            __sql__ = "SHOW FRONTENDS"
            Name = StringField()
            Host = StringField()

        assert hasattr(Frontend, "__sql__")
        assert Frontend.__sql__ == "SHOW FRONTENDS"
        assert Frontend.__table__ == "frontend"
