from __future__ import annotations

import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            user="InstravelApp",
            password="Eo4@;?eaLM",
            database="Instravel",
            port=13306,
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            self.cursor.close()
        finally:
            self.conn.close()

# Singleton simple
_db_singleton: Database | None = None

def get_db() -> Database:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = Database()
    return _db_singleton

def close_db() -> None:
    global _db_singleton
    if _db_singleton is not None:
        _db_singleton.close()
        _db_singleton = None


