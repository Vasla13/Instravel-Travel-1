from __future__ import annotations
from app.backend.database import Database, get_db

class UsersCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_user(self, username: str, mail: str, password: str, nationalite: str | None = None, biographie: str | None = None) -> int:
        # On insère dans la colonne SQL `nationalité`
        sql = """
            INSERT INTO users (username, mail, `nationalité`, password, biographie, status)
            VALUES (%s, %s, %s, %s, %s, 'public')
        """
        self.db.cursor.execute(sql, (username, mail, nationalite, password, biographie))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_user(self, id_user: int) -> dict | None:
        # CORRECTION : On renomme explicitement `nationalité` en 'nationalite'
        sql = """
            SELECT id_user, username, mail, `nationalité` as nationalite, photo, password, biographie, status
            FROM users
            WHERE id_user = %s
        """
        self.db.cursor.execute(sql, (id_user,))
        return self.db.cursor.fetchone()

    def get_user_by_mail_and_password(self, mail: str, password: str) -> dict | None:
        sql = """
            SELECT id_user, username, mail, `nationalité` as nationalite, photo, password, biographie, status
            FROM users 
            WHERE mail = %s AND password = %s
        """
        self.db.cursor.execute(sql, (mail, password))
        return self.db.cursor.fetchone()

    def get_user_by_username(self, username: str) -> dict | None:
        sql = """
            SELECT id_user, username, mail, `nationalité` as nationalite, photo, password, biographie, status
            FROM users
            WHERE username = %s
        """
        self.db.cursor.execute(sql, (username,))
        return self.db.cursor.fetchone()

    def get_users(self) -> list[dict]:
        sql = """
            SELECT id_user, username, mail, `nationalité` as nationalite, photo, password, biographie, status
            FROM users
            ORDER BY id_user DESC
        """
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    def update_user(self, id_user: int, *, username=None, mail=None, nationalite=None, photo=None, password=None, biographie=None):
        sets = []
        values = []

        if username is not None:
            sets.append("username = %s")
            values.append(username)
        if mail is not None:
            sets.append("mail = %s")
            values.append(mail)
        if nationalite is not None:
            # On met à jour la colonne `nationalité` (avec accent)
            sets.append("`nationalité` = %s")
            values.append(nationalite)
        if photo is not None:
            sets.append("photo = %s")
            values.append(photo)
        if password is not None:
            sets.append("password = %s")
            values.append(password)
        if biographie is not None:
            sets.append("biographie = %s")
            values.append(biographie)

        if not sets:
            return False

        sql = f"UPDATE users SET {', '.join(sets)} WHERE id_user = %s"
        values.append(id_user)
        
        try:
            self.db.cursor.execute(sql, values)
            self.db.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur update_user: {e}")
            return False

    def close(self):
        self.db.close()