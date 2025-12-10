import customtkinter as ctk
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.users import UsersCRUD

class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        self.crud_voyages = VoyagesCRUD()
        self.crud_users = UsersCRUD()
        
        self.setup_ui()
        self.load_feed()

    def setup_ui(self):
        # --- NAVBAR (Navigation Commune) ---
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        
        ctk.CTkButton(nav, text="🏠 Mes Voyages", command=lambda: self.master.show_page("ManageTravel"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=10)
        
        ctk.CTkButton(nav, text="🌍 Explorer", fg_color="#333", width=120).pack(side="left", padx=5) # Actif

        ctk.CTkButton(nav, text="👤 Mon Profil", command=lambda: self.master.show_page("Profile"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)
        
        ctk.CTkButton(nav, text="Déconnexion", command=self.master.logout_user, 
                      fg_color="#cf3030", hover_color="#a01010", width=100).pack(side="right", padx=20, pady=10)

        # --- FEED ---
        ctk.CTkLabel(self, text="🌍 Dernières Aventures de la Communauté", font=("Courgette", 30, "bold"), text_color="#00aaff").pack(pady=20)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_feed(self):
        # Récupérer TOUS les voyages (méthode get_voyages existante)
        all_voyages = self.crud_voyages.get_voyages()
        
        if not all_voyages:
            ctk.CTkLabel(self.scroll, text="C'est calme ici... Soyez le premier à poster !", font=("Arial", 16)).pack(pady=50)
            return

        # Grille de cartes (2 colonnes)
        for i, voyage in enumerate(all_voyages):
            self.create_feed_card(voyage)

    def create_feed_card(self, voyage):
        # Récupérer l'auteur
        author = self.crud_users.get_user(voyage['id_user'])
        author_name = author['username'] if author else "Inconnu"

        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="x", pady=10, padx=100)

        # Header: Auteur
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(top, text=f"@{author_name}", font=("Arial", 14, "bold"), text_color="#00aaff").pack(side="left")
        ctk.CTkLabel(top, text="a partagé un voyage", font=("Arial", 12), text_color="gray").pack(side="left", padx=5)

        # Contenu
        ctk.CTkLabel(card, text=voyage['nom_voyage'], font=("Courgette", 22, "bold"), text_color="white").pack(anchor="w", padx=20)
        
        # Dates
        d_txt = "Dates inconnues"
        try: d_txt = f"Du {voyage['date_depart']} au {voyage['date_arrivee']}"
        except: pass
        ctk.CTkLabel(card, text=d_txt, font=("Arial", 12), text_color="#aaa").pack(anchor="w", padx=20, pady=(5, 0))

        # Action: Voir détails
        # Note: Pour l'instant view_travel permet d'éditer (c'est le mode créateur).
        # Dans un vrai Insta, on aurait un "Read Only View". 
        # Pour l'instant on réutilise view_travel mais on pourrait masquer les boutons edit.
        btn = ctk.CTkButton(card, text="Voir le carnet de voyage →", 
                            command=lambda: self.master.show_travel_detail(voyage['id_voyage']),
                            fg_color="#444", hover_color="#555")
        btn.pack(pady=20, padx=20, anchor="e")