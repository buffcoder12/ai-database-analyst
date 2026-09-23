from app.gemini_client import generate_with_fallback
from app.sql_generator import SQLResponse


def correct_sql(
    question: str,
    sql: str,
    error: str,
    schema: dict
):
    """
    Correct a failed PostgreSQL query using
    detailed database schema metadata.
    """

    schema_text = ""

    for table, metadata in schema.items():

        schema_text += (
            f"\nTable: {table}\n"
        )

        schema_text += "Columns:\n"

        for column in metadata["columns"]:

            schema_text += (
                f"- {column['column']} "
                f"({column['type']})\n"
            )

        if metadata["primary_keys"]:

            schema_text += "Primary Keys:\n"

            for key in metadata["primary_keys"]:

                schema_text += (
                    f"- {key}\n"
                )

        if metadata["foreign_keys"]:

            schema_text += "Foreign Keys:\n"

            for foreign_key in metadata[
                "foreign_keys"
            ]:

                schema_text += (
                    f"- {foreign_key['column']} "
                    f"→ "
                    f"{foreign_key['references_table']}."
                    f"{foreign_key['references_column']}\n"
                )

    prompt = f"""
You are an expert PostgreSQL SQL debugging assistant.

The generated SQL query failed during execution.

Fix the SQL query so that it correctly answers
the original user question.

DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

FAILED SQL:
{sql}

DATABASE ERROR:
{error}

RULES:

1. Return a corrected PostgreSQL query.

2. The query must answer the original question.

3. Use ONLY tables and columns from the schema.

4. Never invent columns.

5. Use foreign-key relationships when
   constructing JOINs.

6. Only generate SELECT or WITH queries.

7. Never generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE
   CREATE

8. Do not include markdown code fences.

9. Return only one SQL query.
"""

    response = generate_with_fallback(
        prompt,
        config={
            "temperature": 0.1,
            "response_mime_type": "application/json",
            "response_schema": SQLResponse,
            "tools": []
        }
    )

    if response.text is None:
        raise RuntimeError(
            "Gemini returned an empty response "
            "while correcting SQL."
        )

    return SQLResponse.model_validate_json(
        response.text
    )