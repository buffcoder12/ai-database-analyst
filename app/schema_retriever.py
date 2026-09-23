import re

# Business concept mappings

BUSINESS_CONCEPTS = {

    "revenue": [
        "order_items"
    ],

    "sales": [
        "order_items"
    ],

    "customer": [
        "customers"
    ],

    "customers": [
        "customers"
    ],

    "product": [
        "products"
    ],

    "products": [
        "products"
    ],

    "order": [
        "orders"
    ],

    "orders": [
        "orders"
    ],

    "completed": [
        "orders"
    ],

    "pending": [
        "orders"
    ],

    "cancelled": [
        "orders"
    ]
}


def tokenize(text: str) -> set[str]:
    """
    Convert text into lowercase tokens.
    """

    return set(
        re.findall(
            r"[a-zA-Z_]+",
            text.lower()
        )
    )


def retrieve_relevant_schema(
    question: str,
    schema: dict,
    max_tables: int = 4
):
    """
    Retrieve the most relevant database tables
    for the user's natural-language question.
    """

    question_tokens = tokenize(question)

    table_scores = {}

    #1. Initialize scores

    for table_name in schema:

        table_scores[table_name] = 0

    #2. Table name matching

    for table_name in schema:

        table_tokens = tokenize(
            table_name
        )

        table_scores[table_name] += (
            len(
                question_tokens
                & table_tokens
            ) * 5
        )

    # 3. Column name matching

    for table_name, metadata in schema.items():

        for column in metadata["columns"]:

            column_tokens = tokenize(
                column["column"]
            )

            table_scores[table_name] += (
                len(
                    question_tokens
                    & column_tokens
                ) * 3
            )

    # 4. Business concept matching

    for concept, related_tables in (
        BUSINESS_CONCEPTS.items()
    ):

        if concept in question_tokens:

            for table_name in related_tables:

                if table_name in table_scores:

                    table_scores[table_name] += 10

    # 5. Rank tables

    ranked_tables = sorted(
        table_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    # 6. Select Relevant tables
    selected_tables = [
        table
        for table, score in ranked_tables[:max_tables]
        if score > 0
    ]

    # 7. Add relationship tables ONLY when useful

    question_has_customer = bool(
        question_tokens
        &{
            "customer",
            "customers"
        }
    )

    question_has_product = bool(
        question_tokens
        &{
            "product",
            "products"
        }
    )

    question_has_order = bool(
        question_tokens
        &{
            "order",
            "orders",
            "completed",
            "pending",
            "cancelled"
        }
    )

    # Custommer + order relationship

    if question_has_customer and question_has_order:

        if "customers" in schema:
            selected_tables.append(
                "customers"
            )
        
        if "orders" in schema:
            selected_tables.append(
                "orders"
            )

    
    # Product + revenue relationship

    if question_has_product and (
        "revenue" in question_tokens
        or "sales" in question_tokens
    ):
        
        if "products" in schema:
            selected_tables.append(
                "products"
            )

        if "order_items" in schema:
            selected_tables.append(
                "order_items"
            )

    
    # Remove duplicates (preserving order)

    selected_tables = list(
        dict.fromkeys(
            selected_tables
        )
    )

    # Limit No. of tables

    selected_tables = selected_tables[:max_tables]


    # Fallback

    if not selected_tables:

        selected_tables = [
            table
            for table, _ in ranked_tables[:max_tables]
        ]

    # Final Schema

    relevant_schema = {
        table: schema[table]
        for table in selected_tables
    }

    return relevant_schema