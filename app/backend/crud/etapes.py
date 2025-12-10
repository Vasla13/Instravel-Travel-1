from __future__ import annotations

from app.backend.database import Database, get_db


class EtapesCRUD:
    """CRUD pour la table etapes."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()
    # Dans la classe EtapesCRUD
    def delete_etapes_by_voyage(self, id_voyage: int) -> bool:
        """Supprime toutes les étapes liées à un voyage."""
        # NOTE: Si les étapes ont elles-mêmes des enfants (photos, commentaires), vous devez d'abord les supprimer ici!
        sql = "DELETE FROM etapes WHERE id_voyage = %s"
        self.db.cursor.execute(sql, (id_voyage,))
        self.db.commit()
        return self.db.cursor.rowcount > 0
    def create_etape(
        self,
        nom_etape: str,
        id_voyage: int,
        date_etape: str | None = None,
        description: str | None = None,
        localisation: str | None = None,
        nb_commentaire: int | None = None,
        nb_like: int | None = None,
    ) -> int:
        # Construction dynamique pour laisser le DEFAULT de date_etape si None
        columns = ["nom_etape", "id_voyage"]
        values: list = [nom_etape, id_voyage]
        placeholders = ["%s", "%s"]

        if date_etape is not None:
            columns.append("date_etape")
            values.append(date_etape)
            placeholders.append("%s")
        if description is not None:
            columns.append("description")
            values.append(description)
            placeholders.append("%s")
        if localisation is not None:
            columns.append("localisation")
            values.append(localisation)
            placeholders.append("%s")
        if nb_commentaire is not None:
            columns.append("nb_commentaire")
            values.append(nb_commentaire)
            placeholders.append("%s")
        if nb_like is not None:
            columns.append("nb_like")
            values.append(nb_like)
            placeholders.append("%s")

        sql = f"""
            INSERT INTO etapes ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """
        self.db.cursor.execute(sql, values)
        self.db.commit()
        return self.db.cursor.lastrowid

    def get_etape(self, id_etape: int) -> dict | None:
        sql = """
            SELECT id_etape,
                   nom_etape,
                   date_etape,
                   description,
                   localisation,
                   nb_commentaire,
                   nb_like,
                   id_voyage
            FROM etapes
            WHERE id_etape = %s
        """
        self.db.cursor.execute(sql, (id_etape,))
        return self.db.cursor.fetchone()

    def get_etapes_by_voyage(self, id_voyage: int) -> list[dict]:
        sql = """
            SELECT id_etape,
                   nom_etape,
                   date_etape,
                   description,
                   localisation,
                   nb_commentaire,
                   nb_like,
                   id_voyage
            FROM etapes
            WHERE id_voyage = %s
            ORDER BY date_etape ASC, id_etape ASC
        """
        self.db.cursor.execute(sql, (id_voyage,))
        return self.db.cursor.fetchall()

    def get_etapes_by_localisation(self, localisation: str) -> list[dict]:
        sql = """
            SELECT id_etape,
                   nom_etape,
                   date_etape,
                   description,
                   localisation,
                   nb_commentaire,
                   nb_like,
                   id_voyage
            FROM etapes
            WHERE localisation = %s
            ORDER BY date_etape ASC
        """
        self.db.cursor.execute(sql, (localisation,))
        return self.db.cursor.fetchall()

    def update_etape(
        self,
        id_etape: int,
        *,
        nom_etape: str | None = None,
        date_etape: str | None = None,
        description: str | None = None,
        localisation: str | None = None,
        nb_commentaire: int | None = None,
        nb_like: int | None = None,
        id_voyage: int | None = None,
    ) -> bool:
        field_map = {
            "nom_etape": nom_etape,
            "date_etape": date_etape,
            "description": description,
            "localisation": localisation,
            "nb_commentaire": nb_commentaire,
            "nb_like": nb_like,
            "id_voyage": id_voyage,
        }

        sets: list[str] = []
        values: list = []

        for column, value in field_map.items():
            if value is not None:
                sets.append(f"{column} = %s")
                values.append(value)

        if not sets:
            return False

        sql = f"UPDATE etapes SET {', '.join(sets)} WHERE id_etape = %s"
        values.append(id_etape)
        self.db.cursor.execute(sql, values)
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def delete_etape(self, id_etape: int) -> bool:
        sql = "DELETE FROM etapes WHERE id_etape = %s"
        self.db.cursor.execute(sql, (id_etape,))
        self.db.commit()
        return self.db.cursor.rowcount > 0

    def close(self):
        self.db.close()