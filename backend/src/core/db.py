from ormlambda.databases.my_sql import MySQLRepository
from ormlambda.databases.my_sql.types import MySQLArgs

from .env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)

config: MySQLArgs = {
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_DATABASE,
}
db = MySQLRepository(**config)
