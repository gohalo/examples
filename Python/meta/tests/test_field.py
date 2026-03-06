"""
Tests for Field classes and QueryExpression.
"""
import pytest
from orm.field import (
    Field,
    IntegerField,
    StringField,
    BooleanField,
    JsonField,
    QueryExpression,
    Operator,
)


class TestField:
    """Test base Field class."""

    def test_field_initialization(self):
        field = Field("col_name", "VARCHAR(255)", nullable=False)
        assert field.__column__ == "col_name"
        assert field.field_type == "VARCHAR(255)"
        assert field.nullable is False

    def test_field_defaults(self):
        field = Field(None, "INT")
        assert field.__column__ is None
        assert field.__name__ is None
        assert field.nullable is True


class TestIntegerField:
    """Test IntegerField."""

    def test_integer_field_creation(self):
        field = IntegerField()
        assert field.field_type == "INT"
        assert field.nullable is True

    def test_integer_field_with_name(self):
        field = IntegerField("age", nullable=False)
        assert field.__column__ == "age"
        assert field.nullable is False


class TestStringField:
    """Test StringField."""

    def test_string_field_default_length(self):
        field = StringField()
        assert field.field_type == "VARCHAR(255)"

    def test_string_field_custom_length(self):
        field = StringField("title", length=100)
        assert field.__column__ == "title"
        assert field.field_type == "VARCHAR(100)"

    def test_string_field_not_nullable(self):
        field = StringField(nullable=False)
        assert field.nullable is False


class TestBooleanField:
    """Test BooleanField."""

    def test_boolean_field_creation(self):
        field = BooleanField("is_active")
        assert field.__column__ == "is_active"
        assert field.field_type == "BOOLEAN"


class TestJsonField:
    """Test JsonField."""

    def test_json_field_creation(self):
        field = JsonField("metadata")
        assert field.__column__ == "metadata"
        assert field.field_type == "JSON"


class TestQueryExpression:
    """Test QueryExpression and field operators."""

    def test_eq_operator(self):
        field = StringField("name")
        expr = field == "test"
        assert isinstance(expr, QueryExpression)
        assert expr.field == "name"  # Uses __column__ when __name__ is None
        assert expr.operator == Operator.EQ
        assert expr.value == "test"
        assert expr.to_sql() == "name = 'test'"

    def test_ne_operator(self):
        field = IntegerField("age")
        expr = field != 25
        assert expr.operator == Operator.NE
        assert expr.to_sql() == "age != 25"

    def test_gt_operator(self):
        field = IntegerField("age")
        expr = field > 18
        assert expr.operator == Operator.GT
        assert expr.to_sql() == "age > 18"

    def test_ge_operator(self):
        field = IntegerField("age")
        expr = field >= 18
        assert expr.operator == Operator.GE
        assert expr.to_sql() == "age >= 18"

    def test_lt_operator(self):
        field = IntegerField("age")
        expr = field < 65
        assert expr.operator == Operator.LT
        assert expr.to_sql() == "age < 65"

    def test_le_operator(self):
        field = IntegerField("age")
        expr = field <= 65
        assert expr.operator == Operator.LE
        assert expr.to_sql() == "age <= 65"

    def test_like_operator(self):
        field = StringField("name")
        expr = field.like("%test%")
        assert expr.operator == Operator.LIKE
        assert expr.to_sql() == "name LIKE '%test%'"

    def test_in_operator(self):
        field = IntegerField("id")
        expr = field.in_([1, 2, 3])
        assert expr.operator == Operator.IN
        assert expr.to_sql() == "id IN (1, 2, 3)"

    def test_in_operator_strings(self):
        field = StringField("status")
        expr = field.in_(["active", "pending"])
        assert expr.to_sql() == "status IN ('active', 'pending')"

    def test_not_in_operator(self):
        field = IntegerField("id")
        expr = field.not_in([1, 2, 3])
        assert expr.operator == Operator.NOT_IN
        assert expr.to_sql() == "id NOT IN (1, 2, 3)"

    def test_is_null_operator(self):
        field = StringField("description")
        expr = field.is_null()
        assert expr.operator == Operator.IS_NULL
        assert expr.to_sql() == "description IS NULL"

    def test_is_not_null_operator(self):
        field = StringField("description")
        expr = field.is_not_null()
        assert expr.operator == Operator.IS_NOT_NULL
        assert expr.to_sql() == "description IS NOT NULL"

    def test_in_operator_with_non_list_raises_error(self):
        expr = QueryExpression("field", Operator.IN, "not_a_list")
        with pytest.raises(ValueError, match="should be list or tuple"):
            expr.to_sql()
