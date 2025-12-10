from __future__ import annotations

from app.backend.database import Database, get_db


class EtapeHashtagCRUD:
    """Gestion des relations entre `etapes` et `hashtag` (table de jointure `etape_hashtag`).

    Table: etape_hashtag(id_etape, id_hashtag)
    Aucune clé primaire explicite dans le dump; on considère (id_etape, id_hashtag) comme paire unique logique.
    """

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # CREATE association
    def add_hashtag_to_etape(self, id_etape: int, id_hashtag: int) -> bool:
        # On évite les doublons simples
        if self.exists(id_etape, id_hashtag):
            return False
        sql = "INSERT INTO etape_hashtag (id_etape, id_hashtag) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (id_etape, id_hashtag))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE association
    def remove_hashtag_from_etape(self, id_etape: int, id_hashtag: int) -> bool:
        sql = "DELETE FROM etape_hashtag WHERE id_etape = %s AND id_hashtag = %s"
        self.db.cursor.execute(sql, (id_etape, id_hashtag))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # READ hashtags d'une étape
    def get_hashtags_for_etape(self, id_etape: int) -> list[dict]:
        sql = (
            """
            SELECT h.id_hashtag, h.nom_hashtag
            FROM etape_hashtag eh
            JOIN hashtag h ON h.id_hashtag = eh.id_hashtag
            WHERE eh.id_etape = %s
            ORDER BY h.id_hashtag DESC
            """
        )
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchall()

    # READ étapes d'un hashtag
    def get_etapes_for_hashtag(self, id_hashtag: int) -> list[dict]:
        sql = (
            """
            SELECT e.id_etape, e.nom_etape, e.id_voyage
            FROM etape_hashtag eh
            JOIN etapes e ON e.id_etape = eh.id_etape
            WHERE eh.id_hashtag = %s
            ORDER BY e.id_etape DESC
            """
        )
        self.db.cursor.execute(sql, (id_hashtag,))
        return self.db.cursor.fetchall()

    def exists(self, id_etape: int, id_hashtag: int) -> bool:
        sql = "SELECT 1 FROM etape_hashtag WHERE id_etape = %s AND id_hashtag = %s LIMIT 1"
        self.db.cursor.execute(sql, (id_etape, id_hashtag))
        return self.db.cursor.fetchone() is not None

    def delete_all_for_etape(self, id_etape: int) -> int:
        sql = "DELETE FROM etape_hashtag WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        self.db.commit()
        return self.db.cursor.rowcount

    def delete_all_for_hashtag(self, id_hashtag: int) -> int:
        sql = "DELETE FROM etape_hashtag WHERE id_hashtag = %s"
        self.db.cursor.execute(sql, (id_hashtag,))
        self.db.commit()
        return self.db.cursor.rowcount

    def close(self):
        self.db.close()
