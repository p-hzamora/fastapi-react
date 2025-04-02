from ormlambda.databases.my_sql import MySQLRepository
from src.env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)

db = MySQLRepository(
    **{
        "user": DB_USERNAME,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "database": DB_DATABASE,
    }
)
