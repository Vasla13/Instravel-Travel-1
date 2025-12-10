from __future__ import annotations
import os
from dotenv import load_dotenv
import mysql.connector

# Charge les variables du fichier .env
load_dotenv()

class Database:
    def __init__(self):
        # Utilise les variables d'environnement ou des valeurs par défaut
        self.conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "app_voyage"),
            port=int(os.getenv("DB_PORT", 3306)),
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def commit(self):
        self.conn.commit()

    def close(self):
        try:
            self.cursor.close()
        finally:
            self.conn.close()

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