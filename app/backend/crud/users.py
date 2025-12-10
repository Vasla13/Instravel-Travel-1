from __future__ import annotations
from app.backend.database import Database, get_db

class UsersCRUD:
    """CRUD simple pour la table users."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_user(self, username: str, mail: str, password: str, nationalite: str | None = None, biographie: str | None = None) -> int:
        sql = """
            INSERT INTO users (username, mail, `nationalité`, password, biographie, status)
            VALUES (%s, %s, %s, %s, %s, 'public')
        """
        self.db.cursor.execute(sql, (username, mail, nationalite, password, biographie))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_user_by_mail_and_password(self, mail: str, password: str) -> dict | None:
        """Vérifie les identifiants pour la connexion."""
        sql = """
            SELECT id_user, username, mail, biographie 
            FROM users 
            WHERE mail = %s AND password = %s
        """
        self.db.cursor.execute(sql, (mail, password))
        return self.db.cursor.fetchone()

    def get_user(self, id_user: int) -> dict | None:
        sql = "SELECT * FROM users WHERE id_user = %s"
        self.db.cursor.execute(sql, (id_user,))
        return self.db.cursor.fetchone()

    def get_user_by_username(self, username: str) -> dict | None:
        sql = "SELECT * FROM users WHERE username = %s"
        self.db.cursor.execute(sql, (username,))
        return self.db.cursor.fetchone()
    
    def close(self):
        self.db.close()