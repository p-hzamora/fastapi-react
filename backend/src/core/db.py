from ormlambda import create_engine

from .env import DATABASE_URL


engine = create_engine(DATABASE_URL)
