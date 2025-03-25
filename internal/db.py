from ormlambda.databases.my_sql import MySQLRepository
from backend.env import (
    DB_USERNAME,
    DB_PASSWORD,
    DB_HOST,
    DB_DATABASE,
)

ddbb = MySQLRepository(**{
    "user": DB_USERNAME,
    "password": DB_PASSWORD,
    "host": DB_HOST,
    "database": DB_DATABASE,

})

