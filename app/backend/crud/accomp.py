from __future__ import annotations
from app.backend.database import Database, get_db

class AccompCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def add_accompagnateur(self, id_user: int, id_voyage: int):
        """Ajoute un utilisateur à un voyage."""
        # Vérifie d'abord s'il n'est pas déjà ajouté
        sql_check = "SELECT * FROM accomp WHERE id_user = %s AND id_voyage = %s"
        self.db.cursor.execute(sql_check, (id_user, id_voyage))
        if self.db.cursor.fetchone():
            return # Déjà présent

        sql = "INSERT INTO accomp (id_user, id_voyage) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (id_user, id_voyage))
        self.db.commit()

    def get_accompagnateurs(self, id_voyage: int) -> list[dict]:
        """Récupère la liste des pseudos des accompagnateurs."""
        sql = """
            SELECT u.id_user, u.username, u.photo
            FROM users u
            JOIN accomp a ON u.id_user = a.id_user
            WHERE a.id_voyage = %s
        """
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchall()

    def delete_all_accompagnateurs(self, id_voyage: int):
        """Supprime tous les accompagnateurs d'un voyage (pour le nettoyage)."""
        sql = "DELETE FROM accomp WHERE id_voyage = %s"
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()

    def close(self):
        self.db.close()