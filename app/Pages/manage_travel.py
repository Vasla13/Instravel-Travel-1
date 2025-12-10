import customtkinter as ctk
from PIL import Image
import io
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.photo import PhotosCRUD

class ManageTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_user: int = None):
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        self.crud = VoyagesCRUD()
        self.crud_photo = PhotosCRUD()

        self.setup_ui()
        self.load_travels()

    def setup_ui(self):
        # Navbar
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        ctk.CTkButton(nav, text="🏠 Mes Voyages", fg_color="#333", width=120).pack(side="left", padx=10)
        ctk.CTkButton(nav, text="🌍 Explorer", command=lambda: self.master.show_page("Home"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="👤 Mon Profil", command=lambda: self.master.show_page("Profile"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="Déconnexion", command=self.master.logout_user, fg_color="#cf3030", hover_color="#a01010", width=100).pack(side="right", padx=20, pady=10)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=20)
        ctk.CTkLabel(header, text="Mes Aventures", font=("Courgette", 36, "bold"), text_color="#00aaff").pack(side="left")
        ctk.CTkButton(header, text="+ Créer un Voyage", font=("Arial", 14, "bold"), fg_color="#2CC985", hover_color="#229A65", height=45, command=lambda: self.master.show_page("CreateTravel")).pack(side="right")

        # Zone Grille
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def load_travels(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        try:
            voyages = self.crud.get_voyages_by_user(self.id_user)
        except Exception as e:
            ctk.CTkLabel(self.scroll_frame, text=f"Erreur BDD: {e}").pack()
            return

        if not voyages:
            ctk.CTkLabel(self.scroll_frame, text="Aucun voyage.\nCréez votre première aventure !", font=("Arial", 18)).pack(pady=50)
        else:
            # Logique de GRILLE (2 colonnes)
            column = 0
            row = 0
            # Frame conteneur pour la grille
            grid_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            grid_container.pack(fill="both", expand=True)
            
            for v in voyages:
                self.create_grid_card(v, grid_container, row, column)
                column += 1
                if column > 1: # 2 cartes par ligne
                    column = 0
                    row += 1

    def create_grid_card(self, voyage, parent, r, c):
        # Carte
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#2b2b2b", width=400, height=250)
        card.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
        
        # Configure le grid parent pour que ça s'étende bien
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # 1. Image de couverture (Haut)
        cover_frame = ctk.CTkFrame(card, height=140, corner_radius=15, fg_color="#000")
        cover_frame.pack(fill="x", padx=5, pady=5)
        cover_frame.pack_propagate(False)

        # Récupération photo
        cover_data = self.crud_photo.get_cover_by_voyage(voyage['id_voyage'])
        if cover_data and cover_data['photo']:
            try:
                img = Image.open(io.BytesIO(cover_data['photo']))
                # Image style "Cover" (crop centrée)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 140))
                lbl = ctk.CTkLabel(cover_frame, text="", image=ctk_img)
                lbl.place(x=0, y=0, relwidth=1, relheight=1)
            except: pass
        else:
            ctk.CTkLabel(cover_frame, text="✈️", font=("Arial", 50)).place(relx=0.5, rely=0.5, anchor="center")

        # 2. Infos (Milieu)
        ctk.CTkLabel(card, text=voyage['nom_voyage'], font=("Arial", 18, "bold"), text_color="white").pack(pady=(10,0))
        d_txt = "Dates inconnues"
        try: d_txt = f"{voyage['date_depart']}  ➜  {voyage['date_arrivee']}"
        except: pass
        ctk.CTkLabel(card, text=d_txt, font=("Arial", 12), text_color="gray").pack()

        # 3. Actions (Bas)
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=10)

        ctk.CTkButton(btn_box, text="Ouvrir", width=100, fg_color="#3b8ed0", 
                      command=lambda: self.master.show_travel_detail(voyage['id_voyage'])).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_box, text="✏️", width=40, fg_color="#e6b800", text_color="black",
                      command=lambda: self.master.show_page("EditTravel", id_item=voyage['id_voyage'])).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_box, text="🗑️", width=40, fg_color="#cf3030", 
                      command=lambda: self.confirm_delete(voyage)).pack(side="left", padx=5)

    def confirm_delete(self, voyage):
        msg = CTkMessagebox(title="Supprimer ?", message=f"Supprimer '{voyage['nom_voyage']}' ?", 
                            icon="warning", option_1="Annuler", option_2="Supprimer")
        if msg.get() == "Supprimer":
            if self.crud.delete_voyage(voyage['id_voyage']):
                self.load_travels()