import customtkinter as ctk
from tkcalendar import DateEntry
from CTkMessagebox import CTkMessagebox 
from app.backend.crud.voyages import VoyagesCRUD

class CreateTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_user: int = None): 
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        self.crud_Voyage = VoyagesCRUD()

        self.setup_ui()

    def setup_ui(self):
        # Header Centré
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(pady=40)
        
        ctk.CTkLabel(self.header, text="✈️  Nouveau Voyage", font=("Courgette", 40, "bold"), text_color="#00aaff").pack()

        # Carte Formulaire
        self.card = ctk.CTkFrame(self, width=600, height=400, corner_radius=20, fg_color="#2b2b2b")
        self.card.pack(pady=20)
        self.card.pack_propagate(False) # Garder la taille fixe

        # Nom
        ctk.CTkLabel(self.card, text="Donnez un nom à votre aventure", font=("Arial", 14, "bold"), text_color="#ccc").pack(pady=(40, 5))
        self.name_entry = ctk.CTkEntry(self.card, width=400, height=40, font=("Arial", 16), placeholder_text="Ex: Roadtrip USA 2025")
        self.name_entry.pack(pady=(0, 20))

        # Dates
        date_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        date_frame.pack(pady=20)

        # Début
        f1 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f1.pack(side="left", padx=20)
        ctk.CTkLabel(f1, text="Début", font=("Arial", 12, "bold")).pack(pady=2)
        # Notez les couleurs personnalisées
        self.date_debut = DateEntry(f1, date_pattern="dd/mm/yyyy", width=12, background='#1f6aa5', foreground='white', borderwidth=2)
        self.date_debut.pack()

        # Fin
        f2 = ctk.CTkFrame(date_frame, fg_color="transparent")
        f2.pack(side="left", padx=20)
        ctk.CTkLabel(f2, text="Fin", font=("Arial", 12, "bold")).pack(pady=2)
        self.date_fin = DateEntry(f2, date_pattern="dd/mm/yyyy", width=12, background='#1f6aa5', foreground='white', borderwidth=2)
        self.date_fin.pack()

        # Boutons
        btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        btn_frame.pack(side="bottom", pady=40, fill="x", padx=50)

        ctk.CTkButton(btn_frame, text="Annuler", command=lambda: self.master.show_page("ManageTravel"), 
                      fg_color="transparent", border_width=1, border_color="#555", text_color="#aaa", width=100).pack(side="left")

        ctk.CTkButton(btn_frame, text="Créer le voyage", command=self.create_travel, 
                      fg_color="#00aaff", hover_color="#0077cc", font=("Arial", 14, "bold"), width=200).pack(side="right")

    def create_travel(self):
        name = self.name_entry.get().strip()
        d_start = self.date_debut.get_date()
        d_end = self.date_fin.get_date()

        if not name:
            CTkMessagebox(title="Erreur", message="Le nom est vide.", icon="warning")
            return
        
        if d_start > d_end:
            CTkMessagebox(title="Erreur", message="Dates incohérentes.", icon="warning")
            return

        try:
            self.crud_Voyage.create_voyage(self.id_user, name, d_start.strftime("%Y-%m-%d"), d_end.strftime("%Y-%m-%d"))
            CTkMessagebox(title="Succès", message="Voyage créé !", icon="check")
            self.master.show_page("ManageTravel")
        except Exception as e:
            CTkMessagebox(title="Erreur", message=str(e), icon="cancel")