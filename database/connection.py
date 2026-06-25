import pyodbc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


def get_db_connection():
    try:
        conn = pyodbc.connect(Config.get_connection_string(), timeout=10)
        return conn
    except pyodbc.Error as e:
        raise ConnectionError(f"Database connection failed: {e}")
