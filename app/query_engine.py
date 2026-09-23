from app.schema import get_database_schema
from app.schema_retriever import retrieve_relevant_schema
from app.llm import generate_sql
from app.sql_validator import validate_sql
from app.database import execute_query
from app.answer_generator import generate_answer
from app.chart_generator import generate_visualization
from app.sql_corrector import correct_sql

from app.query_cache import(
    create_cache_key,
    get_cached_result,
    set_cached_result
)

from app.observability import (start_timer, elapsed_time)


def ask_database(question: str):

    # Start timer
    total_start = start_timer()

    # Get database schema
    schema_start = start_timer()
    full_schema = get_database_schema()
    schema_time = elapsed_time(schema_start)

    # Retrieve relevant scehma
    retrieval_start = start_timer()
    relevant_schema = retrieve_relevant_schema(
        question=question,
        schema=full_schema
    )
    retrieval_time = elapsed_time(retrieval_start)

    print("\n" + "=" * 60)
    print("FULL DATABASE SCHEMA")
    print("=" * 60)

    print(list(full_schema.keys()))

    print("\n" + "=" * 60)
    print("RELEVANT SCHEMA")
    print("=" * 60)

    print(list(relevant_schema.keys()))

    # Create cache
    cache_start = start_timer()
    cache_key = create_cache_key(
        question,
        relevant_schema
    )

    cached_result = get_cached_result(
        cache_key
    )
    cache_time = elapsed_time(cache_start)

    if cached_result is not None:

        print("\nCACHE HIT")
        print("Returning cached result.")

        cached_response = {
            **cached_result,
            "from_cache": True
        }

        cached_response[
            "performance"
        ] = {
            "schema_time": schema_time,
            "retrieval_time": retrieval_time,
            "cache_time": cache_time,
            "total_time": elapsed_time(
                total_start
            )
        }

        return cached_response

    print("\nCACHE MISS")
    print("Generating a new result.")

    # Generate SQL
    sql_start = start_timer()
    sql_response = generate_sql(
        question,
        relevant_schema
    )
    sql_time = elapsed_time(sql_start)

    sql = sql_response.sql

    # Validate generated SQL
    validation_start = start_timer()
    validate_sql(sql)

    validation_time = elapsed_time(validation_start)

    # Execute SQL
    execution_start = start_timer()
    correction_attempted = False
    
    try:

        results = execute_query(sql)

    except Exception as error:

        correction_attempted = True

        print("\nSQL execution failed.")
        print("Attempting automatic correction...")

        correction_start = start_timer()

        corrected_response = correct_sql(
            question=question,
            sql=sql,
            error=str(error),
            schema=full_schema
        )
        
        correction_time = elapsed_time(correction_start)

        corrected_sql = (corrected_response.sql)

        # Validate corrected SQL
        validate_sql(corrected_sql)

        # Execute corrected SQL
        results = execute_query(corrected_sql)

        # Replace original SQL information
        sql = corrected_sql
        sql_response = corrected_response
    
    else:
        correction_time = 0.0
    
    execution_time = elapsed_time(execution_start)

    # Generate natural-language answer
    answer_start = start_timer()
    answer = generate_answer(
        question=question,
        sql=sql,
        results=results
    )

    answer_time = elapsed_time(answer_start)

    # Generate visualization
    visualization_start = start_timer()
    visualization = generate_visualization(
        question=question,
        results=results
    )

    visualization_time = elapsed_time(visualization_start)

    # Performance information
    performance = {
        "schema_time": schema_time,
        "retrieval_time": retrieval_time,
        "cache_time": cache_time,
        "sql_generation_time": sql_time,
        "sql_validation_time": validation_time,
        "database_execution_time": execution_time,
        "answer_generation_time": answer_time,
        "visualization_time": visualization_time,
        "correction_time": correction_time,
        "correction_attempted": correction_attempted,
        "total_time": elapsed_time(total_start)
    }

    # Print performance information
    print("\n" + "=" * 60)
    print("PERFORMANCE")
    print("=" * 60)

    for key, value in performance.items():

        print(
            f"{key}: {value}"
        )

    # Build Response
    response = {
        "question": question,
        "sql": sql,
        "explanation": sql_response.explaination,
        "answer": answer,
        "results": results,
        "visualization": visualization,
        "from_cache": False,
        "performance": performance
    }

    # Save Cache
    set_cached_result(
        cache_key,
        response
    )
   
    return response