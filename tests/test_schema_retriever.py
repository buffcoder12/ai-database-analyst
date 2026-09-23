from app.schema_retriever import (
    retrieve_relevant_schema
)


SCHEMA = {
    "customers": {
        "columns": [
            {
                "column": "customer_id",
                "type": "integer",
                "nullable": "NO"
            },
            {
                "column": "name",
                "type": "character varying",
                "nullable": "NO"
            }
        ],
        "primary_keys": [
            "customer_id"
        ],
        "foreign_keys": []
    },

    "orders": {
        "columns": [
            {
                "column": "order_id",
                "type": "integer",
                "nullable": "NO"
            },
            {
                "column": "customer_id",
                "type": "integer",
                "nullable": "NO"
            },
            {
                "column": "status",
                "type": "character varying",
                "nullable": "NO"
            }
        ],
        "primary_keys": [
            "order_id"
        ],
        "foreign_keys": [
            {
                "column": "customer_id",
                "reference_table": "customers",
                "referenced_column": "customer_id"
            }
        ]
    },

    "order_items": {
        "columns": [
            {
                "column": "quantity",
                "type": "integer",
                "nullable": "NO"
            },
            {
                "column": "unit_price",
                "type": "numeric",
                "nullable": "NO"
            }
        ],
        "primary_keys": [],
        "foreign_keys": []
    },

    "products": {
        "columns": [
            {
                "column": "product_id",
                "type": "integer",
                "nullable": "NO"
            },
            {
                "column": "name",
                "type": "character varying",
                "nullable": "NO"
            }
        ],
        "primary_keys": [
            "product_id"
        ],
        "foreign_keys": []
    }
}


def test_revenue_retrieval():

    result = retrieve_relevant_schema(
        "What is the total revenue?",
        SCHEMA
    )

    assert "order_items" in result


def test_customer_order_retrieval():

    result = retrieve_relevant_schema(
        "Which customers have placed orders?",
        SCHEMA
    )

    assert "customers" in result
    assert "orders" in result


def test_product_revenue_retrieval():

    result = retrieve_relevant_schema(
        "What are the top 3 products by revenue?",
        SCHEMA
    )

    assert "products" in result
    assert "order_items" in result


def test_completed_orders_retrieval():

    result = retrieve_relevant_schema(
        "How many orders are completed?",
        SCHEMA
    )

    assert "orders" in result