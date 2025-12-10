from __future__ import annotations

from app.backend.database import Database, get_db


class CommentaireHashtagCRUD:
    """
    Gestion des relations entre `commentaires` et `hashtag`
    (table de jointure supposée: commentaire_hashtag(id_comm, id_hashtag)).

    Adapte l'ancienne logique etape_hashtag -> commentaire_hashtag.
    """

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # CREATE association
    def add_hashtag_to_commentaire(self, id_comm: int, id_hashtag: int) -> bool:
        if self.exists(id_comm, id_hashtag):
            return False
        sql = "INSERT INTO comm_hashtag (id_comm, id_hashtag) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (id_comm, id_hashtag))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE association
    def remove_hashtag_from_commentaire(self, id_comm: int, id_hashtag: int) -> bool:
        sql = "DELETE FROM comm_hashtag WHERE id_comm = %s AND id_hashtag = %s"
        self.db.cursor.execute(sql, (id_comm, id_hashtag))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # READ hashtags d'un commentaire
    def get_hashtags_for_commentaire(self, id_comm: int) -> list[dict]:
        sql = """
            SELECT h.id_hashtag, h.nom_hashtag
            FROM comm_hashtag ch
            JOIN hashtag h ON h.id_hashtag = ch.id_hashtag
            WHERE ch.id_comm = %s
            ORDER BY h.id_hashtag DESC
        """
        self.db.cursor.execute(sql, (id_comm,))
        return self.db.cursor.fetchall()

    # READ commentaires d'un hashtag
    def get_commentaires_for_hashtag(self, id_hashtag: int) -> list[dict]:
        sql = """
            SELECT c.id_comm,
                   c.commentaire,
                   c.date_comm,
                   c.id_user,
                   c.id_etape
            FROM comm_hashtag ch
            JOIN commentaires c ON c.id_comm = ch.id_comm
            WHERE ch.id_hashtag = %s
            ORDER BY c.id_comm DESC
        """
        self.db.cursor.execute(sql, (id_hashtag,))
        return self.db.cursor.fetchall()

    def exists(self, id_comm: int, id_hashtag: int) -> bool:
        sql = """
            SELECT 1
            FROM comm_hashtag
            WHERE id_comm = %s AND id_hashtag = %s
            LIMIT 1
        """
        self.db.cursor.execute(sql, (id_comm, id_hashtag))
        return self.db.cursor.fetchone() is not None

    def delete_all_for_commentaire(self, id_comm: int) -> int:
        sql = "DELETE FROM comm_hashtag WHERE id_comm = %s"
        self.db.cursor.execute(sql, (id_comm,))
        self.db.commit()
        return self.db.cursor.rowcount

    def delete_all_for_hashtag(self, id_hashtag: int) -> int:
        sql = "DELETE FROM comm_hashtag WHERE id_hashtag = %s"
        self.db.cursor.execute(sql, (id_hashtag,))
        self.db.commit()
        return self.db.cursor.rowcount

    def close(self):
        self.db.close()
