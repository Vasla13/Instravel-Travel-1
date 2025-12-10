import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime, date
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD

class EditTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        self.crud = VoyagesCRUD()
        
        # Données du voyage
        self.travel_data = self.crud.get_voyage(self.id_voyage)

        if not self.travel_data:
            ctk.CTkLabel(self, text="Erreur : Voyage introuvable", text_color="red").pack(pady=20)
            ctk.CTkButton(self, text="Retour", command=lambda: self.master.show_page("ManageTravel")).pack()
            return

        self.setup_ui()
        self.prefill_data()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(header, text="← Annuler", command=lambda: self.master.show_page("ManageTravel"), fg_color="#444", width=100).pack(side="left")
        ctk.CTkLabel(header, text="Modifier le Voyage", font=("Courgette", 28, "bold")).pack(side="left", padx=40)

        # Formulaire
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Nom
        ctk.CTkLabel(self.form_frame, text="Nom du voyage", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.name_entry = ctk.CTkEntry(self.form_frame, width=300)
        self.name_entry.pack(anchor="w", padx=20)

        # Dates
        ctk.CTkLabel(self.form_frame, text="Dates", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        dates_row = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        dates_row.pack(anchor="w", padx=20)

        ctk.CTkLabel(dates_row, text="Du : ").pack(side="left")
        self.date_start = DateEntry(dates_row, date_pattern="dd/mm/yyyy", width=12)
        self.date_start.pack(side="left", padx=5)

        ctk.CTkLabel(dates_row, text="Au : ").pack(side="left", padx=(15,0))
        self.date_end = DateEntry(dates_row, date_pattern="dd/mm/yyyy", width=12)
        self.date_end.pack(side="left", padx=5)

        # Bouton Save
        ctk.CTkButton(
            self.form_frame, 
            text="💾 Enregistrer les modifications", 
            fg_color="#e6b800", hover_color="#cc9900", text_color="black",
            height=40, font=("Arial", 14, "bold"),
            command=self.save_changes
        ).pack(pady=40, padx=20, fill="x")

    def prefill_data(self):
        """Remplit les champs avec les données actuelles."""
        # Nom
        self.name_entry.insert(0, self.travel_data['nom_voyage'])
        
        # Dates (Gestion SQL date -> Python date)
        d_start = self.travel_data['date_depart']
        d_end = self.travel_data['date_arrivee']

        if isinstance(d_start, (datetime, date)):
            self.date_start.set_date(d_start)
        if isinstance(d_end, (datetime, date)):
            self.date_end.set_date(d_end)

    def save_changes(self):
        new_name = self.name_entry.get().strip()
        new_start = self.date_start.get_date()
        new_end = self.date_end.get_date()

        if not new_name:
            CTkMessagebox(title="Erreur", message="Le nom ne peut pas être vide.", icon="warning")
            return
        
        if new_start > new_end:
            CTkMessagebox(title="Erreur", message="La date de fin doit être après le début.", icon="warning")
            return

        # Mise à jour BDD
        success = self.crud.update_voyage(
            id_voyage=self.id_voyage,
            nom_voyage=new_name,
            date_depart=new_start.strftime("%Y-%m-%d"),
            date_arrivee=new_end.strftime("%Y-%m-%d")
        )

        if success:
            CTkMessagebox(title="Succès", message="Voyage modifié avec succès !", icon="check")
            self.master.show_page("ManageTravel")
        else:
            CTkMessagebox(title="Erreur", message="Impossible de modifier le voyage.", icon="cancel")