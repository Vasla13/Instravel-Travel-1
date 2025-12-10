from __future__ import annotations
from app.backend.database import Database, get_db

class PhotosCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def add_photo(self, id_etape: int, photo_blob: bytes) -> int:
        """Ajoute une image binaire à une étape."""
        sql = "INSERT INTO photos (id_etape, photo) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (id_etape, photo_blob))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_photo_by_etape(self, id_etape: int) -> dict | None:
        """Récupère la photo d'une étape."""
        sql = "SELECT id_photo, photo FROM photos WHERE id_etape = %s LIMIT 1"
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchone()

    def get_cover_by_voyage(self, id_voyage: int) -> dict | None:
        """
        NOUVEAU : Trouve la première photo disponible dans tout le voyage 
        pour s'en servir de couverture/miniature.
        """
        sql = """
            SELECT p.photo 
            FROM photos p
            JOIN etapes e ON p.id_etape = e.id_etape
            WHERE e.id_voyage = %s
            LIMIT 1
        """
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchone()

    def delete_photos_by_etape(self, id_etape: int) -> bool:
        sql = "DELETE FROM photos WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    
    def close(self):
        self.db.close()