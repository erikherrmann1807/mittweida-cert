import psycopg2

from src.database.config import *


def postgres():
    return psycopg2.connect(database=DB,
                            user=DB_USER,
                            host=DB_HOST,
                            password=DB_PASSWORD,
                            port=DB_PORT)