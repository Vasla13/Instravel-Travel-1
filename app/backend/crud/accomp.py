from __future__ import annotations

from app.backend.database import Database, get_db


class accompCRUD:
    """CRUD simple pour la table accompagnateurs."""


    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # Dans la classe accompCRUD
    def delete_accomp_by_voyage(self, id_voyage: int) -> bool:
        """Supprime toutes les relations accompagnateur-voyage pour un voyage."""
        sql = "DELETE FROM accomp WHERE id_voyage = %s"
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    def create_accompagnateur(
        self,
        id_user: int,
        id_voyage: int,
    ) -> int:
        sql = """
            INSERT INTO accomp (id_user, id_voyage)  /* <-- CORRECTION : utilise 'accomp' */
            VALUES (%s, %s)
        """
        self.db.cursor.execute(sql, (id_user, id_voyage))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_accompagnateur(self, id_accomp: int) -> dict | None:
        sql = """
            SELECT `id_accomp`,
                   id_user,
                   id_voyage
            FROM accomp
            WHERE id_accomp = %s
        """
        self.db.cursor.execute(sql, (id_accomp,))
        return self.db.cursor.fetchall()

    def get_accompagnateurs_by_voyage(self, id_voyage: int) -> list[dict] | None:
        sql = """
            SELECT
                id_user,
                id_voyage
            FROM accomp
            WHERE id_voyage = %s
            ORDER BY id_voyage DESC
        """
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchall()


    def delete_accomp(self, id_accomp: int) -> bool:
        sql = "DELETE FROM accomp WHERE id_accomp = %s"
        self.db.cursor.execute(sql, (id_accomp,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def close(self):
        self.db.close()