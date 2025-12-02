# Server

from fastapi import FastApi
from typing import Dict, Any

import sqlite3

app = FastApi()

DATABASE_NAME = "data.db"

def init_db():
    """
    Initialise the database file.
    """

    try:

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("""

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );

        """)

    except sqlite3.Error as e:
        print("Error mf")
    finally:
        if conn:
            conn.close


init_db()