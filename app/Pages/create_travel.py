import customtkinter as ctk
from tkcalendar import DateEntry
from typing import List, Optional
from datetime import datetime
from CTkMessagebox import CTkMessagebox 
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.accomp import accompCRUD
from app.backend.crud.users import UsersCRUD

class CreateTravelView(ctk.CTkFrame):
    """Page CTkFrame pour créer un voyage."""
    
    def __init__(self, parent, id_user: int = None): 
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user

        self.crud_Voyage = VoyagesCRUD()
        self.crud_Accomp = accompCRUD()
        self.crud_Users = UsersCRUD()
        
        self.escorts: List[str] = []

        if not self.id_user:
             ctk.CTkLabel(self, text="Erreur : Session expirée.", text_color="red").pack(pady=50)
             return

        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkButton(
            header_frame, text="← Retour", 
            command=lambda: self.master.show_page("ManageTravel"),
            width=100, fg_color="#3a3a3a"
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame, text="Nouveau Voyage",
            font=("Courgette", 32, "bold")
        ).pack(side="left", padx=(50, 0), expand=True)

        # Formulaire
        self.scroll = ctk.CTkScrollableFrame(self, width=700, height=400)
        self.scroll.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Nom
        ctk.CTkLabel(self.scroll, text="Nom du Voyage :", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        self.name_entry = ctk.CTkEntry(self.scroll, width=300)
        self.name_entry.pack(anchor="w", padx=20, pady=(5,10))

        # Dates
        date_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        date_frame.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkLabel(date_frame, text="Début :").pack(side="left", padx=5)
        self.date_debut = DateEntry(date_frame, date_pattern="dd/mm/yyyy", width=12)
        self.date_debut.pack(side="left", padx=5)
        
        ctk.CTkLabel(date_frame, text="Fin :").pack(side="left", padx=5)
        self.date_fin = DateEntry(date_frame, date_pattern="dd/mm/yyyy", width=12)
        self.date_fin.pack(side="left", padx=5)

        # Bouton Créer
        ctk.CTkButton(self.scroll, text="Valider la création", command=self.create_travel, height=40, fg_color="green", hover_color="darkgreen").pack(pady=30)

    def create_travel(self):
        name = self.name_entry.get().strip()
        
        # Récupération des objets date
        d_start = self.date_debut.get_date() # Renvoie un objet date python
        d_end = self.date_fin.get_date()

        if not name:
            CTkMessagebox(title="Erreur", message="Le nom du voyage est obligatoire.", icon="warning")
            return
        
        if d_start > d_end:
            CTkMessagebox(title="Erreur", message="La date de fin doit être après la date de début.", icon="warning")
            return

        # Conversion pour MySQL (AAAA-MM-JJ)
        sql_start = d_start.strftime("%Y-%m-%d")
        sql_end = d_end.strftime("%Y-%m-%d")

        try:
            voyage_id = self.crud_Voyage.create_voyage(
                id_user=self.id_user,
                nom_voyage=name,
                date_depart=sql_start,
                date_arrivee=sql_end
            )
            
            # Succès
            msg = CTkMessagebox(title="Succès", message="Voyage créé avec succès !", icon="check", option_1="Voir mes voyages")
            if msg.get() == "Voir mes voyages":
                self.master.show_page("ManageTravel")
            
        except Exception as e:
            CTkMessagebox(title="Erreur BDD", message=f"Impossible de créer le voyage.\n{e}", icon="cancel")