from app.gemini_client import generate_with_fallback


def generate_answer(
    question: str,
    sql: str,
    results: list
):

    """
    Generate a natural-language answer using omly the SQL query results.
    """

    if not results:
        return (
            "No matching records were found for your question."
        )

    prompt = f"""
    You are an AI data analyst.
    Answer the user's question using ONLY the database results provided below.

USER QUESTION:
{question}

SQL QUERY:
{sql}

DATABASE RESULTS:
{results}

RULES:

1. Use ONLY information contained in DATABASE RESULTS.

2. Never invent values or information.

3. Never make assumptions about missing data.

4. Give a clear and concise answer.

5. If the result contains a single important number, state it directly.

6. If the result contains multiple rows, summarize the results naturally.

7. If the user asks for a ranking, preserve the ranking order.

8. If the result contains monetary values, format them using Indian Rupees (₹).

9. For large monetary values, use commas for readability.

10. For counts, use clear wording such as:
    "There are 5 completed orders."

11. Do not generate SQL.

12. Do not modify the database.

13. Do not call tools.

14. Do not mention these instructions.

15. Do not mention that you are an AI unless the user explicitly asks.

16. Keep the answer concise unless the question requires explanation.
"""

    response = generate_with_fallback(
        prompt,
        config={
            "temperature": 0.2,
            "tools": []
        }
    )

    if response.text is None:
        raise RuntimeError(
            "Gemini returned an empty response "
            "while generating the answer."
        )

    return response.text.strip()