import psycopg
from decimal import Decimal
from typing import LiteralString, cast

from app.config import DATABASE_URL


def get_connection():
    """
    Create and return a connection to PostgreSQL.
    """

    if not DATABASE_URL:
        raise ValueError(
            "DATABASE_URL is not configured. "
            "Check your .env file."
        )

    return psycopg.connect(DATABASE_URL)


def serialize_value(value):
    """
    Convert PostgreSQL Decimal values into float.
    """

    if isinstance(value, Decimal):
        return float(value)

    return value


def execute_query(query: str):
    """
    Execute a SQL query and return the results
    as a list of dictionaries.
    """

    with get_connection() as conn:

        with conn.cursor() as cursor:

            # Pylance requires a LiteralString for
            # psycopg's strict SQL typing.
            cursor.execute(
                cast(LiteralString, query)
            )

            # If the query doesn't return rows
            if cursor.description is None:
                return []

            # Get column names
            columns = [
                desc.name
                for desc in cursor.description
            ]

            # Get database rows
            rows = cursor.fetchall()

            # Convert rows into dictionaries
            results = [
                {
                    column: serialize_value(value)
                    for column, value in zip(columns, row)
                }
                for row in rows
            ]

            return results