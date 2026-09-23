from pprint import pprint

from app.schema import get_database_schema
from app.schema_retriever import (
    retrieve_relevant_schema
)


schema = get_database_schema()


questions = [
    "What is the total revenue?",
    "Which customers have placed orders?",
    "What are the top 3 products by revenue?",
    "How many orders are completed?"
]


for question in questions:

    print("\n" + "=" * 60)

    print(
        f"QUESTION: {question}"
    )

    print("=" * 60)

    relevant_schema = (
        retrieve_relevant_schema(
            question,
            schema
        )
    )

    pprint(relevant_schema)