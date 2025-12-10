import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime, date
from CTkMessagebox import CTkMessagebox
from app.backend.crud.etapes import EtapesCRUD

class EditStageView(ctk.CTkFrame):
    def __init__(self, parent, etape_id: int):
        super().__init__(parent)
        self.master = parent
        self.etape_id = etape_id
        self.crud = EtapesCRUD()

        self.etape_data = self.crud.get_etape(self.etape_id)
        
        # Liste de villes
        self.villes_populaires = [
            "Paris, France", "Marseille, France", "Lyon, France", 
            "Londres, UK", "New York, USA", "Tokyo, Japon", 
            "Rome, Italie", "Barcelone, Espagne", "Berlin, Allemagne"
        ]

        if not self.etape_data:
            ctk.CTkLabel(self, text="Erreur: Étape introuvable").pack()
            return

        self.setup_ui()
        self.prefill_data()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(header, text="← Annuler", command=lambda: self.master.show_travel_detail(self.etape_data['id_voyage']), 
                      fg_color="#444", width=100).pack(side="left")
        ctk.CTkLabel(header, text="✏️ Modifier l'Étape", font=("Courgette", 28, "bold"), text_color="#FFC107").pack(side="left", padx=30)

        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Card
        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="x", padx=10, pady=10)

        # Nom
        ctk.CTkLabel(card, text="Titre", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_nom = ctk.CTkEntry(card, width=400, height=40, font=("Arial", 14))
        self.entry_nom.pack(anchor="w", padx=20)

        # Date & Lieu
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(anchor="w", padx=20, pady=20, fill="x")

        col_date = ctk.CTkFrame(row, fg_color="transparent")
        col_date.pack(side="left")
        ctk.CTkLabel(col_date, text="Date", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", pady=(0,5))
        self.entry_date = DateEntry(col_date, date_pattern="dd/mm/yyyy", width=12)
        self.entry_date.pack()

        col_lieu = ctk.CTkFrame(row, fg_color="transparent")
        col_lieu.pack(side="left", padx=(40, 0))
        ctk.CTkLabel(col_lieu, text="Lieu", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", pady=(0,5))
        self.entry_lieu = ctk.CTkComboBox(col_lieu, width=300, height=40, values=self.villes_populaires, font=("Arial", 14))
        self.entry_lieu.pack()

        # Description
        ctk.CTkLabel(card, text="Description", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_desc = ctk.CTkTextbox(card, width=500, height=120, corner_radius=10, font=("Arial", 13))
        self.entry_desc.pack(anchor="w", padx=20, fill="x", expand=True, pady=(0, 20))

        # Bouton
        ctk.CTkButton(card, text="💾  Sauvegarder", command=self.save_changes, 
                      fg_color="#e6b800", hover_color="#cfa500", text_color="black", height=50, font=("Arial", 16, "bold")).pack(pady=(10, 30), padx=20, fill="x")

    def prefill_data(self):
        self.entry_nom.insert(0, self.etape_data['nom_etape'])
        if self.etape_data['localisation']:
            self.entry_lieu.set(self.etape_data['localisation'])
        if self.etape_data['description']:
            self.entry_desc.insert("1.0", self.etape_data['description'])
        d = self.etape_data['date_etape']
        if isinstance(d, (datetime, date)):
            self.entry_date.set_date(d)

    def save_changes(self):
        nom = self.entry_nom.get().strip()
        lieu = self.entry_lieu.get().strip()
        desc = self.entry_desc.get("1.0", "end").strip()
        date_obj = self.entry_date.get_date()
        date_sql = date_obj.strftime("%Y-%m-%d")

        if not nom:
            CTkMessagebox(title="Erreur", message="Titre obligatoire", icon="warning")
            return

        if self.crud.update_etape(self.etape_id, nom, date_sql, desc, lieu):
            self.master.show_travel_detail(self.etape_data['id_voyage'])
        else:
            CTkMessagebox(title="Erreur", message="Échec modification", icon="cancel")