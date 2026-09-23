import re
import sqlparse
from sqlparse.sql import Comment
from sqlparse.tokens import Keyword


ALLOWED_STATEMENTS = {"SELECT", "WITH"}


FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE"
}

def remove_comments(query: str) -> str:
    """
    Remove SQL comments before validation.
    """

    statements = sqlparse.parse(query)

    cleaned_parts = []

    for statement in statements:
        for token in statement.tokens:

            if isinstance(token, Comment):
                continue

            cleaned_parts.append(str(token))

    return "".join(cleaned_parts)



def validate_sql(query: str) -> bool:
    """
    Validate that the SQL query is a single, read-only SELECT or WITH statement.
    """

    if not isinstance(query, str):
        raise ValueError("SQL query must be a string.")

    query = query.strip()

    if not query:
        raise ValueError("SQL query is empty.")

    # Parse SQL
    statements = sqlparse.parse(query)

    if len(statements) != 1:
        raise ValueError(
            "Only one SQL statement is allowed."
        )

    statement = statements[0]

    # Remove comments for Keyword inspection

    cleaned_query = remove_comments(query)

    # Check forbidden SQL keywords

    for keyword in FORBIDDEN_KEYWORDS:

        pattern = rf"\b{keyword}\b"

        if re.search(pattern, cleaned_query, re.IGNORECASE):

            raise ValueError( f"Forbidden SQL keyword detected: {keyword}" )

    
    # Find first meaningful SQL token

    first_token = None

    for token in statement.tokens:

        if token.is_whitespace:
            continue

        if token.ttype in (sqlparse.tokens.Newline,):
            continue

        first_token = token
        break

    if first_token is None:
        raise ValueError("Invalid SQL.")

    keyword = first_token.value.upper().strip()

    # Determine statement type
   
    statement_type = (statement.get_type().upper())
   
    if statement_type not in ALLOWED_STATEMENTS:

        raise ValueError(
            "Only SELECT or WITH queries are allowed."
        )

    return True