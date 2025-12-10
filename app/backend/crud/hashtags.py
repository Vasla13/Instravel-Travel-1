from __future__ import annotations

from app.backend.database import Database, get_db


class HashtagsCRUD:
    """CRUD simple pour la table `hashtag`.

    Colonnes: id_hashtag (AUTO_INCREMENT), nom_hashtag (varchar(15) NOT NULL)
    """

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # CREATE
    def create_hashtag(self, nom_hashtag: str) -> int:
        sql = "INSERT INTO hashtag (nom_hashtag) VALUES (%s)"
        self.db.cursor.execute(sql, (nom_hashtag,))
        self.db.commit()
        return self.db.cursor.lastrowid

    # READ (one)
    def get_hashtag(self, id_hashtag: int) -> dict | None:
        sql = "SELECT id_hashtag, nom_hashtag FROM hashtag WHERE id_hashtag = %s"
        self.db.cursor.execute(sql, (id_hashtag,))
        return self.db.cursor.fetchone()
    
    # READ by exact name
    def get_by_name(self, name: str) -> dict | None:
        sql = "SELECT id_hashtag, nom_hashtag FROM hashtag WHERE nom_hashtag = %s LIMIT 1"
        self.db.cursor.execute(sql, (name,))
        return self.db.cursor.fetchone()
    def delete_etape_hashtags_by_voyage(self, id_voyage: int) -> bool:
        """
        Supprime toutes les relations etape_hashtag pour toutes les étapes d'un voyage donné.
        (Nécessite une jointure pour trouver les étapes liées au voyage).
        """
        sql = """
            DELETE eh FROM etape_hashtag eh
            JOIN etapes e ON eh.id_etape = e.id_etape
            WHERE e.id_voyage = %s
        """
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    # GET or CREATE by name, returns id_hashtag
    def get_or_create(self, name: str) -> int:
        row = self.get_by_name(name)
        if row:
            return int(row["id_hashtag"]) if isinstance(row, dict) else int(row[0])
        return self.create_hashtag(name)

    # Search by name
    def search_hashtags_By_Name(self, name: str):
        sql = "SELECT id_hashtag, nom_hashtag FROM hashtag WHERE nom_hashtag LIKE %s"
        self.db.cursor.execute(sql, (f"%{name}%",))
        return self.db.cursor.fetchall()

    # READ (all)
    def get_hashtags(self) -> list[dict]:
        sql = "SELECT id_hashtag, nom_hashtag FROM hashtag ORDER BY id_hashtag DESC"
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    # UPDATE
    def update_hashtag(self, id_hashtag: int, *, nom_hashtag: str | None = None) -> bool:
        if nom_hashtag is None:
            return False
        sql = "UPDATE hashtag SET nom_hashtag = %s WHERE id_hashtag = %s"
        self.db.cursor.execute(sql, (nom_hashtag, id_hashtag))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE
    def delete_hashtag(self, id_hashtag: int) -> bool:
        sql = "DELETE FROM hashtag WHERE id_hashtag = %s"
        self.db.cursor.execute(sql, (id_hashtag,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def close(self):  # cohérence avec autres CRUD
        self.db.close()
