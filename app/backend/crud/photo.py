from __future__ import annotations

from app.backend.database import Database, get_db


"""CRUD pour la table `photos`.

Schéma (dump):
	photos(
		id_photo INT AUTO_INCREMENT PRIMARY KEY,
		lien_photo VARCHAR(25) NOT NULL,
		id_etape INT NOT NULL FK -> etapes.id_etape
	)

Fonctions fournies:
	- create_photo(lien_photo, id_etape) -> int
	- get_photo(id_photo) -> dict | None
	- get_photos_by_etape(id_etape) -> list[dict]
	- update_photo(id_photo, lien_photo=None, id_etape=None) -> bool
	- delete_photo(id_photo) -> bool
	- delete_photos_for_etape(id_etape) -> int
"""

from app.backend.database import Database, get_db


class PhotosCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # CREATE : stocke un blob
    def create_photo(self, photo_blob: bytes, id_etape: int) -> int:
        sql = "INSERT INTO photos (photo, id_etape) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (photo_blob, id_etape))
        self.db.commit()
        return self.db.cursor.lastrowid

    # READ one
    def get_photo(self, id_photo: int) -> dict | None:
        sql = "SELECT id_photo, photo, id_etape FROM photos WHERE id_photo = %s"
        self.db.cursor.execute(sql, (id_photo,))
        return self.db.cursor.fetchone()

    # READ many by étape
    def get_photos_by_etape(self, id_etape: int) -> list[dict]:
        sql = "SELECT id_photo, photo, id_etape FROM photos WHERE id_etape = %s ORDER BY id_photo DESC"
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchall()

    # UPDATE
    def update_photo(self, id_photo: int, *, photo_blob: bytes | None = None, id_etape: int | None = None) -> bool:
        fields, values = [], []
        if photo_blob is not None:
            fields.append("photo = %s")
            values.append(photo_blob)
        if id_etape is not None:
            fields.append("id_etape = %s")
            values.append(id_etape)
        if not fields:
            return False
        values.append(id_photo)
        sql = f"UPDATE photos SET {', '.join(fields)} WHERE id_photo = %s"
        self.db.cursor.execute(sql, tuple(values))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE
    def delete_photo(self, id_photo: int) -> bool:
        sql = "DELETE FROM photos WHERE id_photo = %s"
        self.db.cursor.execute(sql, (id_photo,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE all for étape
    def delete_photos_for_etape(self, id_etape: int) -> int:
        sql = "DELETE FROM photos WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        self.db.commit()
        return self.db.cursor.rowcount
    # Dans app/backend/crud/photo.py (classe PhotosCRUD)
    def get_first_photo_blob_by_etape(self, id_etape: int) -> bytes | None:
        """
        Récupère le BLOB de la première photo associée à une étape.
        Utilisé pour l'aperçu dans ViewTravelView.
        """
        sql = """
            SELECT photo
            FROM photos
            WHERE id_etape = %s
            ORDER BY id_photo ASC
            LIMIT 1
        """
        self.db.cursor.execute(sql, (id_etape,))
        result = self.db.cursor.fetchone()
        
        # Retourne le BLOB (bytes) ou None
        return result['photo'] if result and 'photo' in result else None
    def delete_photos_by_voyage(self, id_voyage: int) -> bool:
            """
            Supprime toutes les photos liées aux étapes d'un voyage donné.
            Utilise une jointure pour cibler les photos via l'ID du voyage.
            """
            sql = """
                DELETE p FROM photos p
                JOIN etapes e ON p.id_etape = e.id_etape
                WHERE e.id_voyage = %s
            """
        
            self.db.cursor.execute(sql, (id_voyage,))
            self.db.commit()
            return self.db.cursor.rowcount > 0
    
    def close(self):
        self.db.close()
