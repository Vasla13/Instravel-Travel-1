from __future__ import annotations

from app.backend.database import Database, get_db


class UsersCRUD:
    """CRUD simple pour la table users (avec biographie)."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_user(
        self,
        username: str,
        mail: str,
        nationalite: str | None = None,
        photo: str | None = None,
        password: str | None = None,
        biographie: str | None = None,
    ) -> int:
        sql = """
            INSERT INTO users (username, mail, `nationalité`, photo, password, biographie)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.db.cursor.execute(sql, (username, mail, nationalite, photo, password, biographie))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_user(self, id_user: int) -> dict | None:
        sql = """
            SELECT id_user,
                   username,
                   mail,
                   `nationalité` AS nationalite,
                   photo,
                   password,
                   biographie
            FROM users
            WHERE id_user = %s
        """
        self.db.cursor.execute(sql, (id_user,))
        return self.db.cursor.fetchone()

    def get_user_by_username(self, username: str) -> dict | None:
        sql = """
            SELECT id_user,
                   username,
                   mail,
                   `nationalité` AS nationalite,
                   photo,
                   password,
                   biographie
            FROM users
            WHERE username = %s
            LIMIT 1
        """
        self.db.cursor.execute(sql, (username,))
        return self.db.cursor.fetchone()

    def get_users(self) -> list[dict]:
        sql = """
            SELECT id_user,
                   username,
                   mail,
                   `nationalité` AS nationalite,
                   photo,
                   password,
                   biographie
            FROM users
            ORDER BY id_user DESC
        """
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    def update_user(
        self,
        id_user: int,
        *,
        username: str | None = None,
        mail: str | None = None,
        nationalite: str | None = None,
        photo: str | None = None,
        password: str | None = None,
        biographie: str | None = None,
    ) -> bool:
        field_map = {
            "username": "username",
            "mail": "mail",
            "nationalite": "`nationalité`",
            "photo": "photo",
            "password": "password",
            "biographie": "biographie",
        }
        values: list = []
        sets: list[str] = []

        if username is not None:
            sets.append(f"{field_map['username']} = %s")
            values.append(username)
        if mail is not None:
            sets.append(f"{field_map['mail']} = %s")
            values.append(mail)
        if nationalite is not None:
            sets.append(f"{field_map['nationalite']} = %s")
            values.append(nationalite)
        if photo is not None:
            sets.append(f"{field_map['photo']} = %s")
            values.append(photo) 
        if password is not None:
            sets.append(f"{field_map['password']} = %s")
            values.append(password)
        if biographie is not None:
            sets.append(f"{field_map['biographie']} = %s")
            values.append(biographie)

        if not sets:
            return False

        sql = f"UPDATE users SET {', '.join(sets)} WHERE id_user = %s"
        values.append(id_user)
        self.db.cursor.execute(sql, values)
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def delete_user(self, id_user: int) -> bool:
        # Purge des relations d'abonnement avant suppression pour éviter les contraintes FK
        try:
            from backend.crud.abonnement import AbonnementCRUD
            AbonnementCRUD(self.db).purge_user(id_user)
        except Exception:
            pass  # purge best-effort
        sql = "DELETE FROM users WHERE id_user = %s"
        self.db.cursor.execute(sql, (id_user,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    
    def close(self):
        self.db.close()
