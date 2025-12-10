import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD

class ManageTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_user: int = None):
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        self.crud = VoyagesCRUD()

        self.setup_ui()
        self.load_travels()

    def setup_ui(self):
        # --- NAVBAR ---
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        
        ctk.CTkButton(nav, text="🏠 Mes Voyages", fg_color="#333", width=120).pack(side="left", padx=10) # Actif
        
        ctk.CTkButton(nav, text="🌍 Explorer", command=lambda: self.master.show_page("Home"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)

        ctk.CTkButton(nav, text="👤 Mon Profil", command=lambda: self.master.show_page("Profile"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)
        
        ctk.CTkButton(nav, text="Déconnexion", command=self.master.logout_user, 
                      fg_color="#cf3030", hover_color="#a01010", width=100).pack(side="right", padx=20, pady=10)

        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=30)

        ctk.CTkLabel(header, text="Mes Aventures", font=("Courgette", 36, "bold"), text_color="#00aaff").pack(side="left")

        ctk.CTkButton(header, text="+ Nouveau Voyage", font=("Arial", 14, "bold"),
                      fg_color="#2CC985", hover_color="#229A65", height=45,
                      command=lambda: self.master.show_page("CreateTravel")).pack(side="right")

        # --- LISTE ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_travels(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        try:
            voyages = self.crud.get_voyages_by_user(self.id_user)
        except Exception as e:
            ctk.CTkLabel(self.scroll_frame, text=f"Erreur BDD: {e}").pack()
            return

        if not voyages:
            ctk.CTkLabel(self.scroll_frame, text="Vous n'avez pas encore de voyage.\nCréez-en un maintenant !", font=("Arial", 16)).pack(pady=50)
        else:
            for v in voyages:
                self.create_card(v)

    def create_card(self, voyage):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#2b2b2b")
        card.pack(fill="x", padx=100, pady=10)

        # Info
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=20, pady=15, fill="both", expand=True)
        ctk.CTkLabel(info, text=voyage['nom_voyage'], font=("Arial", 20, "bold")).pack(anchor="w")
        
        d_txt = "Dates inconnues"
        try: d_txt = f"Du {voyage['date_depart']} au {voyage['date_arrivee']}"
        except: pass
        ctk.CTkLabel(info, text=d_txt, text_color="#aaa").pack(anchor="w")

        # Actions
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="right", padx=20)

        ctk.CTkButton(actions, text="Voir", width=80, fg_color="#3b8ed0", 
                      command=lambda: self.master.show_travel_detail(voyage['id_voyage'])).pack(side="left", padx=5)
        
        ctk.CTkButton(actions, text="✏️", width=40, fg_color="#e6b800", text_color="black",
                      command=lambda: self.master.show_page("EditTravel", id_item=voyage['id_voyage'])).pack(side="left", padx=5)
        
        ctk.CTkButton(actions, text="🗑️", width=40, fg_color="#cf3030", 
                      command=lambda: self.confirm_delete(voyage)).pack(side="left", padx=5)

    def confirm_delete(self, voyage):
        msg = CTkMessagebox(title="Supprimer ?", message=f"Supprimer '{voyage['nom_voyage']}' ?", 
                            icon="warning", option_1="Annuler", option_2="Supprimer")
        if msg.get() == "Supprimer":
            if self.crud.delete_voyage(voyage['id_voyage']):
                self.load_travels()