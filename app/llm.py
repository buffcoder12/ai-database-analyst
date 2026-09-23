from app.sql_generator import SQLResponse
from app.gemini_client import generate_with_fallback


def generate_sql(
    question: str,
    schema: dict
):
    """
    Generate PostgreSQL SQL from a natural-language
    question using the relevant database schema.
    """

    schema_text = ""

    for table, metadata in schema.items():

        schema_text += f"\nTable: {table}\n"

      
        # Columns

        schema_text += "Columns:\n"

        for column in metadata["columns"]:

            schema_text += (
                f"- {column['column']} "
                f"({column['type']}, "
                f"nullable={column['nullable']})\n"
            )


        # Primary Keys
       
        if metadata["primary_keys"]:

            schema_text += "Primary Keys:\n"

            for key in metadata["primary_keys"]:
                schema_text += f"- {key}\n"

        
        # Foreign Keys

        if metadata["foreign_keys"]:

            schema_text += "Foreign Keys:\n"

            for foreign_key in metadata["foreign_keys"]:

                schema_text += (
                    f"- {foreign_key['column']} "
                    f"→ "
                    f"{foreign_key['reference_table']}."
                    f"{foreign_key['referenced_column']}\n"
                )

    
    # SQL generation prompt
 
    prompt = f"""
You are an expert PostgreSQL SQL generator
for an AI-powered database analyst.

Your job is to convert the user's natural-language
question into ONE correct PostgreSQL query.

RELEVANT DATABASE SCHEMA:
{schema_text}

USER QUESTION:
{question}

RULES:

1. Generate ONLY one SQL query.

2. The query must be either:
   - SELECT
   - WITH ... SELECT

3. NEVER generate:
   INSERT
   UPDATE
   DELETE
   DROP
   ALTER
   TRUNCATE
   CREATE
   GRANT
   REVOKE

4. Use ONLY tables and columns present in the provided schema.

5. NEVER invent a table or column.

6. Use foreign-key relationships when a JOIN is required.

7. Do NOT add unnecessary JOINs.

8. If the question can be answered using one table, prefer one table.

9. For revenue calculations, use: quantity * unit_price

10. For total revenue use: SUM(quantity * unit_price)

11. When the user asks for revenue by product, join order_items with products using: order_items.product_id = products.product_id

12. When grouping results, every selected non-aggregated column must appear in GROUP BY.

13. Use COUNT() when the user asks: how many, number of, count

14. Use SUM() when the user asks:
    - total
    - revenue
    - sales amount

15. Use AVG() when the user asks:
    - average
    - mean

16. Use MAX() when the user asks:
    - highest
    - maximum
    - largest

17. Use MIN() when the user asks:
    - lowest
    - minimum
    - smallest

18. Use ORDER BY when the user asks for:
    - top
    - highest
    - lowest
    - ranking

19. Use LIMIT when the user specifies
    a number such as:
    - top 3
    - top 5
    - first 10

20. When filtering order status, use the orders.status column.

21. For completed orders, use: WHERE status = 'Completed'

22. Use appropriate aliases to make aggregate columns readable.

23. Do not use SELECT * unless the user explicitly asks for all columns.

24. Do not include Markdown code fences.

25. Do not include explanations inside the SQL query.

26. Return SQL that directly answers the user's question.

IMPORTANT:

The database schema provided above may contain foreign keys that are not necessary for the current question.

Only JOIN tables when the user's question actually requires information from those tables.

Return a single valid PostgreSQL query.
"""


    # Generate structured response
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
            "Gemini returned an empty response."
        )

    return SQLResponse.model_validate_json(
        response.text
    )