from pprint import pprint
from app.schema import get_database_schema

schema = get_database_schema()
pprint(schema)
