from ormlambda import create_engine

from .env import DATABASE_URL, URI_DB_CONNECTION, DB_DATABASE


no_db_con = create_engine(URI_DB_CONNECTION)

if not no_db_con.schema_exists(DB_DATABASE):
    no_db_con.create_schema(DB_DATABASE)


engine = create_engine(DATABASE_URL)
