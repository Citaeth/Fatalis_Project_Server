import psycopg2
from psycopg2 import OperationalError
from flask_app.config import Config

def get_db_connection():
    """
    basic connection to the database.
    :return:
    """
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
        return conn
    except OperationalError as e:
        print(f"database connection error : {e}")
        return None

def test_connection():
    """
    function to test the connection to the database.
    :return:
    """
    conn = get_db_connection()
    if conn:
        print("Well connected to the database!.")
        conn.close()
    else:
        print("Connection to the database failed.")