from app.schema import get_database_schema
from app.sql_generator import SQLResponse
from app.llm import generate_sql


schema = get_database_schema()

question = "Who are the top 3 customers by total spending?"

result = generate_sql(question, schema)

print("\nGENERATED SQL")
print("=============")

print(result.sql)

print("\nEXPLANATION")
print("===========")

print(result.explaination)