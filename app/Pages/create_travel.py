import customtkinter as ctk
from tkcalendar import DateEntry
from CTkMessagebox import CTkMessagebox 
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.users import UsersCRUD
from app.backend.crud.accomp import AccompCRUD

class CreateTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_user: int = None): 
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        
        self.crud_voyage = VoyagesCRUD()
        self.crud_user = UsersCRUD()
        self.crud_accomp = AccompCRUD()
        
        self.added_friends = [] # Liste temporaire des amis ajoutés

        self.setup_ui()

    def setup_ui(self):
        # --- NAVBAR ---
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        ctk.CTkButton(nav, text="🏠 Mes Voyages", command=lambda: self.master.show_page("ManageTravel"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=10)
        ctk.CTkButton(nav, text="👤 Mon Profil", command=lambda: self.master.show_page("Profile"), fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)

        # --- TITRE ---
        ctk.CTkLabel(self, text="✈️  Créer une Aventure", font=("Courgette", 32, "bold"), text_color="#00aaff").pack(pady=(30, 20))

        # --- CARTE FORMULAIRE ---
        card = ctk.CTkFrame(self, width=800, height=500, corner_radius=20, fg_color="#2b2b2b")
        card.pack(pady=10, fill="y") 

        # Colonne Gauche : Infos Base
        left_col = ctk.CTkFrame(card, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(left_col, text="Nom du voyage", font=("Arial", 14, "bold"), text_color="#ddd").pack(anchor="w", pady=(0, 5))
        self.entry_name = ctk.CTkEntry(left_col, width=300, height=40, font=("Arial", 14), placeholder_text="Ex: Roadtrip Italie")
        self.entry_name.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(left_col, text="Dates", font=("Arial", 14, "bold"), text_color="#ddd").pack(anchor="w", pady=(0, 5))
        
        # Frame Dates
        d_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        d_frame.pack(anchor="w")
        
        self.date_start = DateEntry(d_frame, width=12, background='#1f6aa5', foreground='white', borderwidth=2)
        self.date_start.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(d_frame, text="➜", text_color="gray").pack(side="left")
        
        self.date_end = DateEntry(d_frame, width=12, background='#1f6aa5', foreground='white', borderwidth=2)
        self.date_end.pack(side="left", padx=(10, 0))

        # Colonne Droite : Compagnons
        right_col = ctk.CTkFrame(card, fg_color="#222", corner_radius=15)
        right_col.pack(side="right", fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(right_col, text="👥 Compagnons de voyage", font=("Arial", 14, "bold"), text_color="#00aaff").pack(pady=(15, 10))
        
        # Zone Ajout
        add_box = ctk.CTkFrame(right_col, fg_color="transparent")
        add_box.pack(fill="x", padx=15)
        self.entry_friend = ctk.CTkEntry(add_box, placeholder_text="Pseudo...", width=150)
        self.entry_friend.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(add_box, text="+", width=40, command=self.add_friend, fg_color="#3b8ed0").pack(side="right", padx=5)

        # Liste des amis (Scrollable)
        self.friend_list_frame = ctk.CTkScrollableFrame(right_col, fg_color="transparent", height=150)
        self.friend_list_frame.pack(fill="both", expand=True, padx=5, pady=10)
        
        # CORRECTION ICI : Suppression du paramètre 'fx' inutile
        self.lbl_empty = ctk.CTkLabel(self.friend_list_frame, text="Aucun compagnon ajouté", font=("Arial", 12), text_color="gray")
        self.lbl_empty.pack(pady=20)

        # --- BOUTONS ACTION (Bas) ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)

        ctk.CTkButton(btn_frame, text="Annuler", command=lambda: self.master.show_page("ManageTravel"), 
                      fg_color="transparent", border_width=1, border_color="#555", text_color="#aaa").pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Créer le voyage", command=self.create_travel, 
                      fg_color="#2CC985", hover_color="#229A65", height=45, font=("Arial", 15, "bold"), width=200).pack(side="left", padx=10)

    def add_friend(self):
        pseudo = self.entry_friend.get().strip()
        if not pseudo: return

        user = self.crud_user.get_user_by_username(pseudo)
        
        if not user:
            CTkMessagebox(title="Introuvable", message=f"L'utilisateur '{pseudo}' n'existe pas.", icon="warning")
            return
        
        if user['id_user'] == self.id_user:
            CTkMessagebox(title="Erreur", message="Vous faites déjà partie du voyage !", icon="info")
            return

        for f in self.added_friends:
            if f['id_user'] == user['id_user']:
                return 

        self.added_friends.append(user)
        self.entry_friend.delete(0, "end")
        self.refresh_friend_list()

    def refresh_friend_list(self):
        for w in self.friend_list_frame.winfo_children(): w.destroy()
        
        if not self.added_friends:
            ctk.CTkLabel(self.friend_list_frame, text="Aucun compagnon ajouté", font=("Arial", 12), text_color="gray").pack(pady=20)
            return

        for i, friend in enumerate(self.added_friends):
            row = ctk.CTkFrame(self.friend_list_frame, fg_color="#333", corner_radius=10)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"👤 {friend['username']}", font=("Arial", 12)).pack(side="left", padx=10)
            ctk.CTkButton(row, text="✕", width=25, height=25, fg_color="transparent", text_color="red", hover_color="#444",
                          command=lambda idx=i: self.remove_friend(idx)).pack(side="right")

    def remove_friend(self, idx):
        del self.added_friends[idx]
        self.refresh_friend_list()

    def create_travel(self):
        name = self.entry_name.get().strip()
        d_start = self.date_start.get_date()
        d_end = self.date_end.get_date()

        if not name:
            CTkMessagebox(title="Erreur", message="Nom du voyage requis.", icon="warning")
            return

        if d_start > d_end:
            CTkMessagebox(title="Erreur", message="Dates incohérentes.", icon="warning")
            return

        try:
            voyage_id = self.crud_voyage.create_voyage(self.id_user, name, d_start.strftime("%Y-%m-%d"), d_end.strftime("%Y-%m-%d"))
            
            for friend in self.added_friends:
                self.crud_accomp.add_accompagnateur(friend['id_user'], voyage_id)

            CTkMessagebox(title="Succès", message="Voyage créé avec succès !", icon="check")
            self.master.show_page("ManageTravel")
            
        except Exception as e:
            CTkMessagebox(title="Erreur Système", message=str(e), icon="cancel")