import customtkinter as ctk
from tkcalendar import DateEntry
from CTkMessagebox import CTkMessagebox
from app.backend.crud.etapes import EtapesCRUD

class CreateStageView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        self.crud = EtapesCRUD()
        
        # Liste de villes pour l'aide à la saisie
        self.villes_populaires = [
            "Paris, France", "Marseille, France", "Lyon, France", 
            "Londres, UK", "New York, USA", "Tokyo, Japon", 
            "Rome, Italie", "Barcelone, Espagne", "Berlin, Allemagne", 
            "Sydney, Australie", "Dubai, UAE", "Rio de Janeiro, Brésil",
            "Amsterdam, Pays-Bas", "Lisbonne, Portugal", "Bangkok, Thaïlande"
        ]

        self.setup_ui()

    def setup_ui(self):
        # 1. Header (Fixe en haut)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(header, text="← Retour", command=lambda: self.master.show_travel_detail(self.id_voyage), 
                      fg_color="#444", width=100).pack(side="left")
        
        ctk.CTkLabel(header, text="✨ Nouvelle Étape", font=("Courgette", 28, "bold"), text_color="#00aaff").pack(side="left", padx=30)

        # 2. Zone de contenu Scrollable (Pour être sûr de voir le bouton en bas)
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Carte blanche/grise pour le formulaire
        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="x", padx=10, pady=10)

        # --- Champs du formulaire ---
        
        # Titre
        ctk.CTkLabel(card, text="Titre de l'étape *", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_nom = ctk.CTkEntry(card, width=400, placeholder_text="Ex: Visite du Louvre", height=40, font=("Arial", 14))
        self.entry_nom.pack(anchor="w", padx=20)

        # Groupe Date & Lieu
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(anchor="w", padx=20, pady=20, fill="x")

        # Date
        col_date = ctk.CTkFrame(row, fg_color="transparent")
        col_date.pack(side="left")
        ctk.CTkLabel(col_date, text="Date", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", pady=(0,5))
        self.entry_date = DateEntry(col_date, date_pattern="dd/mm/yyyy", width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_date.pack()

        # Lieu (ComboBox pour auto-complétion)
        col_lieu = ctk.CTkFrame(row, fg_color="transparent")
        col_lieu.pack(side="left", padx=(40, 0))
        ctk.CTkLabel(col_lieu, text="Lieu (Ville, Pays)", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", pady=(0,5))
        
        # CTkComboBox permet de choisir OU d'écrire ce qu'on veut
        self.entry_lieu = ctk.CTkComboBox(col_lieu, width=300, height=40, values=self.villes_populaires, font=("Arial", 14))
        self.entry_lieu.set("") # Vide par défaut
        self.entry_lieu.pack()

        # Description
        ctk.CTkLabel(card, text="Notes & Description", font=("Arial", 14, "bold"), text_color="#eee").pack(anchor="w", padx=20, pady=(15, 5))
        self.entry_desc = ctk.CTkTextbox(card, width=500, height=120, corner_radius=10, font=("Arial", 13))
        self.entry_desc.pack(anchor="w", padx=20, fill="x", expand=True, pady=(0, 20))

        # --- BOUTON VALIDER (Bien visible en bas de la carte) ---
        self.btn_save = ctk.CTkButton(
            card, 
            text="✅  Enregistrer l'étape", 
            command=self.save_stage, 
            fg_color="#2CC985", 
            hover_color="#229A65", 
            height=50, 
            font=("Arial", 16, "bold")
        )
        self.btn_save.pack(pady=(10, 30), padx=20, fill="x")

    def save_stage(self):
        nom = self.entry_nom.get().strip()
        lieu = self.entry_lieu.get().strip()
        desc = self.entry_desc.get("1.0", "end").strip()
        date_obj = self.entry_date.get_date()
        date_sql = date_obj.strftime("%Y-%m-%d")

        if not nom:
            CTkMessagebox(title="Erreur", message="Le titre de l'étape est obligatoire.", icon="warning")
            return

        try:
            self.crud.create_etape(self.id_voyage, nom, date_sql, desc, lieu)
            self.master.show_travel_detail(self.id_voyage)
        except Exception as e:
            CTkMessagebox(title="Erreur", message=f"Erreur lors de la sauvegarde : {e}", icon="cancel")