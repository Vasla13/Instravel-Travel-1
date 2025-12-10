from __future__ import annotations

from app.backend.database import Database, get_db


class likesCRUD:
    """CRUD simple pour la table likes."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_like(
        self,
        id_user: int,
        id_etape: int,
    ) -> int:
        sql = """
            INSERT INTO likes (id_user, id_etape)
            VALUES (%s, %s)
        """
        self.db.cursor.execute(sql, (id_user, id_etape))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_like(self, id_like: int) -> dict | None:
        sql = """
            SELECT id_like,
                   id_user,
                   id_etape
            FROM likes
            WHERE id_like = %s
        """
        self.db.cursor.execute(sql, (id_like,))
        return self.db.cursor.fetchall()

    def get_likes_by_etape(self, id_etape: int) -> list[dict] | None:
        sql = """
            SELECT id_like,
                   id_user,
                   id_etape
            FROM likes
            WHERE id_etape = %s
            ORDER BY id_like DESC
        """
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchall()

    def delete_like(self, id_like: int) -> bool:
        sql = "DELETE FROM likes WHERE id_like = %s"
        self.db.cursor.execute(sql, (id_like,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def close(self):
        self.db.close()