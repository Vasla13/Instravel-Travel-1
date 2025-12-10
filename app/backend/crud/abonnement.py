from __future__ import annotations

"""CRUD pour la table `abonnement` (relations de suivi entre utilisateurs).

Table (simpliste) :
    abonnement(id_user1 INT NOT NULL, id_user2 INT NOT NULL)

Convention :
    - id_user1 suit id_user2 (follower -> followed)
    - Pas de clé primaire déclarée dans le dump, on considère (id_user1, id_user2) comme unique.
"""

from app.backend.database import Database, get_db


class AbonnementCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    # CREATE (follow)
    def follow(self, follower_id: int, followed_id: int) -> bool:
        if follower_id == followed_id:
            return False  # auto-follow interdit
        if self.is_following(follower_id, followed_id):
            return False  # déjà suivi
        sql = "INSERT INTO abonnement (id_user1, id_user2) VALUES (%s, %s)"
        self.db.cursor.execute(sql, (follower_id, followed_id))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # DELETE (unfollow)
    def unfollow(self, follower_id: int, followed_id: int) -> bool:
        sql = "DELETE FROM abonnement WHERE id_user1 = %s AND id_user2 = %s"
        self.db.cursor.execute(sql, (follower_id, followed_id))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # READ: est-ce que follower_id suit followed_id ?
    def is_following(self, follower_id: int, followed_id: int) -> bool:
        sql = (
            "SELECT 1 FROM abonnement WHERE id_user1 = %s AND id_user2 = %s LIMIT 1"
        )
        self.db.cursor.execute(sql, (follower_id, followed_id))
        return self.db.cursor.fetchone() is not None

    # READ: followers d'un user (ceux qui le suivent)
    def get_followers(self, user_id: int) -> list[dict]:
        sql = (
            """
            SELECT u.id_user, u.username, u.mail
            FROM abonnement a
            JOIN users u ON u.id_user = a.id_user1
            WHERE a.id_user2 = %s
            ORDER BY u.id_user DESC
            """
        )
        self.db.cursor.execute(sql, (user_id,))
        return self.db.cursor.fetchall()

    # READ: comptes suivis par user (following)
    def get_following(self, user_id: int) -> list[dict]:
        sql = (
            """
            SELECT u.id_user, u.username, u.mail
            FROM abonnement a
            JOIN users u ON u.id_user = a.id_user2
            WHERE a.id_user1 = %s
            ORDER BY u.id_user DESC
            """
        )
        self.db.cursor.execute(sql, (user_id,))
        return self.db.cursor.fetchall()

    # Compter followers
    def count_followers(self, user_id: int) -> int:
        sql = "SELECT COUNT(*) AS c FROM abonnement WHERE id_user2 = %s"
        self.db.cursor.execute(sql, (user_id,))
        row = self.db.cursor.fetchone()
        return int(row["c"]) if row else 0

    # Compter following
    def count_following(self, user_id: int) -> int:
        sql = "SELECT COUNT(*) AS c FROM abonnement WHERE id_user1 = %s"
        self.db.cursor.execute(sql, (user_id,))
        row = self.db.cursor.fetchone()
        return int(row["c"]) if row else 0

    # Mutualité (follow réciproque) pour permetre le privé public
    def is_mutual(self, user_a: int, user_b: int) -> bool:
        return self.is_following(user_a, user_b) and self.is_following(user_b, user_a)

    # Liste des mutuals pour un user (option simple)
    def get_mutuals(self, user_id: int) -> list[dict]:
        sql = (
            """
            SELECT u.id_user, u.username, u.mail
            FROM abonnement a
            JOIN abonnement b ON a.id_user2 = b.id_user1 AND b.id_user2 = a.id_user1
            JOIN users u ON u.id_user = a.id_user2
            WHERE a.id_user1 = %s
            ORDER BY u.id_user DESC
            """
        )
        self.db.cursor.execute(sql, (user_id,))
        return self.db.cursor.fetchall()

    # Suppression totale des liens d'un user (utilitaire)
    def purge_user(self, user_id: int) -> int:
        sql = "DELETE FROM abonnement WHERE id_user1 = %s OR id_user2 = %s"
        self.db.cursor.execute(sql, (user_id, user_id))
        self.db.commit()
        return self.db.cursor.rowcount

    def close(self):
        self.db.close()
