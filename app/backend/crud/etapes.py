from __future__ import annotations
from app.backend.database import Database, get_db

class EtapesCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_etape(self, id_voyage: int, nom: str, date_etape: str, description: str = "", localisation: str = "") -> int:
        sql = """
            INSERT INTO etapes (nom_etape, date_etape, description, localisation, id_voyage, nb_commentaire, nb_like)
            VALUES (%s, %s, %s, %s, %s, 0, 0)
        """
        self.db.cursor.execute(sql, (nom, date_etape, description, localisation, id_voyage))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_etapes_by_voyage(self, id_voyage: int) -> list[dict]:
        sql = """
            SELECT * FROM etapes 
            WHERE id_voyage = %s 
            ORDER BY date_etape ASC
        """
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchall()

    def get_etape(self, id_etape: int) -> dict | None:
        sql = "SELECT * FROM etapes WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchone()

    def update_etape(self, id_etape: int, nom: str, date_etape: str, description: str, localisation: str) -> bool:
        sql = """
            UPDATE etapes 
            SET nom_etape=%s, date_etape=%s, description=%s, localisation=%s
            WHERE id_etape=%s
        """
        self.db.cursor.execute(sql, (nom, date_etape, description, localisation, id_etape))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def delete_etape(self, id_etape: int) -> bool:
        """Suppression en cascade propre."""
        try:
            # Nettoyage des dépendances
            self.db.cursor.execute("DELETE FROM photos WHERE id_etape = %s", (id_etape,))
            self.db.cursor.execute("DELETE FROM commentaires WHERE id_etape = %s", (id_etape,))
            self.db.cursor.execute("DELETE FROM likes WHERE id_etape = %s", (id_etape,))
            self.db.cursor.execute("DELETE FROM etape_hashtag WHERE id_etape = %s", (id_etape,))
            
            # Suppression de l'étape
            self.db.cursor.execute("DELETE FROM etapes WHERE id_etape = %s", (id_etape,))
            self.db.commit()
            return self.db.cursor.rowcount > 0
        except Exception as e:
            print(f"Erreur delete_etape: {e}")
            return False