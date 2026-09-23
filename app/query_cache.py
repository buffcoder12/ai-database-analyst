from functools import cache
import hashlib 
import time 


# Maximum number of cached queries
MAX_CACHE_SIZE = 50

# Cache lifetime: 1 hour
CACHE_TTL = 60 * 60

_cache = {}


def normalize_question(question: str) -> str:
    """
    Normalize a user's question so that small formatting
    differences do not create different cache entries.
    """

    return " ".join(
        question.lower().strip().split()
    )

def create_cache_key(
    question: str,
    schema: dict
) -> str:
    """
    Create a cache key using:
    - normalized question
    - relevant database schema

    This prevents the same question against different schemas drom sharing a cache entry.
    """

    normalized_question = normalize_question(
        question
    ) 

    schema_text = str(
        sorted(
            (
                table,
                tuple(
                    (
                        column["column"],
                        column["type"],
                        column["nullable"]
                    )
                    for column in metadata["columns"]
                ),
                tuple(
                    sorted(
                        metadata["primary_keys"]
                    )
                ),
                tuple(
                    sorted(
                        (
                            foreign_key["column"],
                            foreign_key["reference_table"],
                            foreign_key["referenced_column"]
                        )
                        for foreign_key in metadata["foreign_keys"]
                    )
                )
            )
            for table, metadata in schema.items()
        )
    )
    
    raw_key = (
        normalized_question
        + "|"
        + schema_text
    )

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def get_cached_result(cache_key: str):
    """
    Retrieve a cached result if it exists and has not expired.
    """

    if cache_key not in _cache:
        return None
    
    cached_item = _cache[cache_key]

    created_time = cached_item["time"]

    if time.time() - created_time > CACHE_TTL:
        del _cache[cache_key]
        return None
    
    return cached_item["result"]


def set_cached_result(
    cache_key: str,
    result
):

    """
    Store a result in the cache.
    If the cahche is full, remove the oldest entry.
    """

    # Remove oldest entry if cache is full
    if(
        len(_cache) >= MAX_CACHE_SIZE
        and cache_key not in _cache
    ):
        
        oldest_key = min(
            _cache,
            key=lambda key: -_cache[key]["time"]
        )

        del _cache[oldest_key]

    _cache[cache_key] = {
        "time": time.time(),
        "result": result
    }

def clear_cache():
    """
    Clear all cached results.
    """

    _cache.clear()


def get_cache_size() -> int:
    """
    Return the number of cached queries.
    """

    return len(_cache)