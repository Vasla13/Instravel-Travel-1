from __future__ import annotations

"""CRUD pour la table `commentaires`.

Schéma (dump):
    commentaires(
        id_comm INT AUTO_INCREMENT PRIMARY KEY,
        commentaire LONGTEXT NOT NULL,
        date_comm DATETIME DEFAULT CURRENT_TIMESTAMP,
        id_user INT NOT NULL,
        id_etape INT NOT NULL,
        id_hashtag INT NULL (optionnel dans dump mais nous gérons via table de jointure comm_hashtag)
    )

On n'utilise pas id_hashtag ici afin de privilégier la table de jointure `comm_hashtag`.
"""

from typing import List, Optional
from app.backend.database import Database, get_db


class CommentairesCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_commentaire(self, commentaire: str, id_user: int, id_etape: int) -> int:
        sql = (
            """
            INSERT INTO commentaires (commentaire, id_user, id_etape)
            VALUES (%s, %s, %s)
            """
        )
        self.db.cursor.execute(sql, (commentaire, id_user, id_etape))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_commentaire(self, id_comm: int) -> dict | None:
        sql = (
            """
            SELECT id_comm, commentaire, date_comm, id_user, id_etape
            FROM commentaires
            WHERE id_comm = %s
            """
        )
        self.db.cursor.execute(sql, (id_comm,))
        return self.db.cursor.fetchone()

    def get_commentaires_for_etape(self, id_etape: int) -> List[dict]:
        sql = (
            """
            SELECT id_comm, commentaire, date_comm, id_user, id_etape
            FROM commentaires
            WHERE id_etape = %s
            ORDER BY id_comm DESC
            """
        )
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchall()

    def delete_commentaire(self, id_comm: int) -> bool:
        sql = "DELETE FROM commentaires WHERE id_comm = %s"
        self.db.cursor.execute(sql, (id_comm,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    # Dans la classe CommentairesCRUD
    def delete_commentaires_by_voyage(self, id_voyage: int) -> bool:
        """Supprime tous les commentaires pour un voyage donné (en joignant les étapes)."""
        # Joindre étapes et commentaires pour trouver tous les commentaires du voyage
        sql = """
            DELETE c FROM commentaires c
            JOIN etapes e ON c.id_etape = e.id_etape
            WHERE e.id_voyage = %s
        """
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    def close(self):
        self.db.close()