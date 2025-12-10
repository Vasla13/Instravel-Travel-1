from __future__ import annotations
from app.backend.database import Database, get_db

class LikesCRUD:
    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def toggle_like(self, id_user: int, id_etape: int) -> bool:
        """
        Ajoute le like s'il n'existe pas, ou le supprime s'il existe (bascule).
        Retourne True si l'utilisateur aime maintenant l'étape, False sinon.
        """
        # 1. Vérifier si déjà liké
        sql_check = "SELECT id_like FROM likes WHERE id_user = %s AND id_etape = %s"
        self.db.cursor.execute(sql_check, (id_user, id_etape))
        existing = self.db.cursor.fetchone()

        if existing:
            # Suppression (Unlike)
            self.db.cursor.execute("DELETE FROM likes WHERE id_like = %s", (existing['id_like'],))
            liked = False
        else:
            # Ajout (Like)
            self.db.cursor.execute("INSERT INTO likes (id_user, id_etape) VALUES (%s, %s)", (id_user, id_etape))
            liked = True
        
        self.db.commit()
        
        # 2. Mettre à jour le compteur dans la table etapes (pour un affichage rapide)
        self.update_stats(id_etape)
        
        return liked

    def is_liked(self, id_user: int, id_etape: int) -> bool:
        """Vérifie si un utilisateur a liké une étape."""
        sql = "SELECT id_like FROM likes WHERE id_user = %s AND id_etape = %s"
        self.db.cursor.execute(sql, (id_user, id_etape))
        return self.db.cursor.fetchone() is not None

    def get_count(self, id_etape: int) -> int:
        """Compte les likes réels."""
        sql = "SELECT COUNT(*) as total FROM likes WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        res = self.db.cursor.fetchone()
        return res['total'] if res else 0

    def update_stats(self, id_etape: int):
        count = self.get_count(id_etape)
        sql = "UPDATE etapes SET nb_like = %s WHERE id_etape = %s"
        self.db.cursor.execute(sql, (count, id_etape))
        self.db.commit()
        
    def close(self):
        self.db.close()