import pytest

from app.sql_validator import validate_sql


def test_valid_select():

    assert validate_sql(
        "SELECT * FROM customers"
    ) is True


def test_valid_with_query():

    assert validate_sql(
        """
        WITH totals AS (
            SELECT SUM(quantity) AS total
            FROM order_items
        )
        SELECT *
        FROM totals
        """
    ) is True


def test_reject_insert():

    with pytest.raises(ValueError):

        validate_sql(
            """
            INSERT INTO customers
            (name)
            VALUES ('Test')
            """
        )


def test_reject_update():

    with pytest.raises(ValueError):

        validate_sql(
            """
            UPDATE customers
            SET name = 'Test'
            """
        )


def test_reject_delete():

    with pytest.raises(ValueError):

        validate_sql(
            """
            DELETE FROM customers
            """
        )


def test_reject_drop():

    with pytest.raises(ValueError):

        validate_sql(
            """
            DROP TABLE customers
            """
        )


def test_reject_multiple_statements():

    with pytest.raises(ValueError):

        validate_sql(
            """
            SELECT *
            FROM customers;

            DELETE FROM customers;
            """
        )


def test_created_at_is_allowed():

    assert validate_sql(
        """
        SELECT created_at
        FROM customers
        """
    ) is True