from pydantic import BaseModel, Field


class SQLResponse(BaseModel):

    sql: str = Field(
        description="A valid PostgreSQL SELECT query"
    )

    explaination: str = Field(
        description="Short explanation of what the query does"
    )
    
