from __future__ import annotations
from app.backend.database import Database, get_db
from typing import List, Optional

class VoyagesCRUD:
    """CRUD pour la table voyages."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_voyage(self, id_user: int, nom_voyage: str | None = None,
                      date_depart: str | None = None, date_arrivee: str | None = None) -> int:
        sql = (
            """
            INSERT INTO voyages (nom_voyage, `date_départ`, `date_arrivée`, id_user)
            VALUES (%s, %s, %s, %s)
            """
        )
        self.db.cursor.execute(sql, (nom_voyage, date_depart, date_arrivee, id_user))
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_voyage(self, id_voyage: int) -> dict | None:
        sql = (
            """
            SELECT id_voyage, nom_voyage, `date_départ` AS date_depart, `date_arrivée` AS date_arrivee, id_user
            FROM voyages
            WHERE id_voyage = %s
            """
        )
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchone()

    # --- NOUVELLE MÉTHODE REQUISE POUR LA GESTION ---
    def get_voyages_by_user(self, id_user: int) -> list[dict]:
        """Récupère tous les voyages créés par un utilisateur spécifique."""
        sql = """
            SELECT id_voyage, nom_voyage, `date_départ` AS date_depart, `date_arrivée` AS date_arrivee, id_user
            FROM voyages
            WHERE id_user = %s
            ORDER BY date_depart DESC
        """
        self.db.cursor.execute(sql, (id_user,))
        return self.db.cursor.fetchall()
    # ----------------------------------------------------

    def get_voyages(self) -> list[dict]:
        sql = (
            """
            SELECT id_voyage, nom_voyage, `date_départ` AS date_depart, `date_arrivée` AS date_arrivee, id_user
            FROM voyages
            ORDER BY id_voyage DESC
            """
        )
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    def update_voyage(self, id_voyage: int, *, nom_voyage: str | None = None, id_user: int | None = None,
                       date_depart: str | None = None, date_arrivee: str | None = None) -> bool:
        field_map = {
            "nom_voyage": "nom_voyage",
            "id_user": "id_user",
            "date_depart": "`date_départ`",
            "date_arrivee": "`date_arrivée`",
        }
        values: list = []
        sets: list[str] = []

        if nom_voyage is not None:
            sets.append(f"{field_map['nom_voyage']} = %s")
            values.append(nom_voyage)
        if id_user is not None:
            sets.append(f"{field_map['id_user']} = %s")
            values.append(id_user)
        if date_depart is not None:
            sets.append(f"{field_map['date_depart']} = %s")
            values.append(date_depart)
        if date_arrivee is not None:
            sets.append(f"{field_map['date_arrivee']} = %s")
            values.append(date_arrivee)

        if not sets:
            return False

        sql = f"UPDATE voyages SET {', '.join(sets)} WHERE id_voyage = %s"
        values.append(id_voyage)
        self.db.cursor.execute(sql, values)
        self.db.commit()
        return self.db.cursor.rowcount > 0

    # --- MÉTHODE REQUISE POUR LA SUPPRESSION ---
    def delete_voyage(self, id_voyage: int) -> bool:
        sql = "DELETE FROM voyages WHERE id_voyage = %s"
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def close(self):
        self.db.close()