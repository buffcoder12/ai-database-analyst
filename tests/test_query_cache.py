from app.query_cache import (
    create_cache_key,
    set_cached_result,
    get_cached_result,
    clear_cache,
    get_cache_size
)


SCHEMA = {
    "orders": {
        "columns": [
            {
                "column": "order_id",
                "type": "integer",
                "nullable": "NO"
            }
        ],
        "primary_keys": [
            "order_id"
        ],
        "foreign_keys": []
    }
}


def test_same_question_same_cache_key():

    key1 = create_cache_key(
        "What is the total revenue?",
        SCHEMA
    )

    key2 = create_cache_key(
        "  what is the total revenue?  ",
        SCHEMA
    )

    assert key1 == key2


def test_different_questions_different_keys():

    key1 = create_cache_key(
        "What is the total revenue?",
        SCHEMA
    )

    key2 = create_cache_key(
        "How many orders are there?",
        SCHEMA
    )

    assert key1 != key2


def test_cache_store_and_retrieve():

    clear_cache()

    key = create_cache_key(
        "test question",
        SCHEMA
    )

    result = {
        "answer": "test"
    }

    set_cached_result(
        key,
        result
    )

    cached = get_cached_result(
        key
    )

    assert cached == result


def test_clear_cache():

    clear_cache()

    assert get_cache_size() == 0