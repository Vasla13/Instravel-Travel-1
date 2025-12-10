import customtkinter as ctk
from PIL import Image
import io
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.users import UsersCRUD
from app.backend.crud.photo import PhotosCRUD

class HomePage(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.master = parent
        self.crud_voyages = VoyagesCRUD()
        self.crud_users = UsersCRUD()
        self.crud_photo = PhotosCRUD()
        
        self.all_voyages = [] # Stockage local pour filtrage rapide
        
        self.setup_ui()
        self.load_feed()

    def setup_ui(self):
        # Navbar
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        ctk.CTkButton(nav, text="🏠 Mes Voyages", command=lambda: self.master.show_page("ManageTravel"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=10)
        ctk.CTkButton(nav, text="🌍 Explorer", fg_color="#333", width=120).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="👤 Mon Profil", command=lambda: self.master.show_page("Profile"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="Déconnexion", command=self.master.logout_user, fg_color="#cf3030", hover_color="#a01010", width=100).pack(side="right", padx=20, pady=10)

        # Header Recherche
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=20)
        
        ctk.CTkLabel(header, text="🌍 Explorer le monde", font=("Courgette", 32, "bold"), text_color="#00aaff").pack(side="left")
        
        # Barre de recherche
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.filter_feed) # Appelle le filtre à chaque frappe
        
        self.entry_search = ctk.CTkEntry(header, width=300, height=40, placeholder_text="🔍 Chercher un voyage, une destination...", textvariable=self.search_var)
        self.entry_search.pack(side="right")

        # Scroll Feed
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_feed(self):
        # On charge tout au début
        self.all_voyages = self.crud_voyages.get_voyages()
        self.display_grid(self.all_voyages)

    def filter_feed(self, *args):
        """Filtre les voyages selon le texte de recherche."""
        query = self.search_var.get().lower()
        if not query:
            self.display_grid(self.all_voyages)
            return

        filtered = []
        for v in self.all_voyages:
            # Recherche dans le nom du voyage
            if query in v['nom_voyage'].lower():
                filtered.append(v)
                continue
            
            # Recherche dans le pseudo de l'auteur
            author = self.crud_users.get_user(v['id_user'])
            if author and query in author['username'].lower():
                filtered.append(v)
        
        self.display_grid(filtered)

    def display_grid(self, voyages_list):
        # Nettoyage
        for w in self.scroll.winfo_children(): w.destroy()
        
        if not voyages_list:
            ctk.CTkLabel(self.scroll, text="Aucun résultat.", font=("Arial", 16), text_color="gray").pack(pady=50)
            return

        # Grille 3 colonnes
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)

        col, row = 0, 0
        for v in voyages_list:
            self.create_feed_card(v, grid, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def create_feed_card(self, voyage, parent, r, c):
        author = self.crud_users.get_user(voyage['id_user'])
        author_name = author['username'] if author else "Inconnu"

        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="#222")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent", height=40)
        top.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(top, text=f"@{author_name}", font=("Arial", 12, "bold"), text_color="#00aaff").pack(side="left")

        cover_frame = ctk.CTkFrame(card, height=180, fg_color="black", corner_radius=0)
        cover_frame.pack(fill="x")
        cover_frame.pack_propagate(False)

        cover = self.crud_photo.get_cover_by_voyage(voyage['id_voyage'])
        if cover and cover['photo']:
            try:
                img = Image.open(io.BytesIO(cover['photo']))
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(350, 180))
                ctk.CTkLabel(cover_frame, text="", image=ctk_img).place(relx=0.5, rely=0.5, anchor="center")
            except: pass
        else:
            ctk.CTkLabel(cover_frame, text="🗺️", font=("Arial", 40)).place(relx=0.5, rely=0.5, anchor="center")

        bottom = ctk.CTkFrame(card, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(bottom, text=voyage['nom_voyage'], font=("Courgette", 20, "bold"), anchor="w").pack(fill="x")
        
        ctk.CTkButton(bottom, text="Voir le carnet →", fg_color="transparent", border_width=1, border_color="#555", 
                      command=lambda: self.master.show_travel_detail(voyage['id_voyage'])).pack(pady=(10,0), fill="x")