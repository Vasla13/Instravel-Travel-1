import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime, date
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.users import UsersCRUD
from app.backend.crud.accomp import AccompCRUD

class EditTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        
        self.crud = VoyagesCRUD()
        self.crud_user = UsersCRUD()
        self.crud_accomp = AccompCRUD()
        
        self.travel_data = self.crud.get_voyage(self.id_voyage)
        # Charger les amis existants depuis la BDD
        self.current_friends = self.crud_accomp.get_accompagnateurs(self.id_voyage)

        if not self.travel_data: return
        self.setup_ui()
        self.prefill_data()

    def setup_ui(self):
        # Navbar simplifiée
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(header, text="← Retour", command=lambda: self.master.show_page("ManageTravel"), fg_color="#444", width=100).pack(side="left")
        ctk.CTkLabel(header, text="Modifier le Voyage", font=("Courgette", 28, "bold"), text_color="#FFC107").pack(side="left", padx=30)

        card = ctk.CTkFrame(self, width=800, corner_radius=20, fg_color="#2b2b2b")
        card.pack(pady=10, fill="both", expand=True, padx=40)

        # GAUCHE : Infos
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(left, text="Nom", font=("Arial", 13, "bold"), text_color="gray").pack(anchor="w")
        self.entry_name = ctk.CTkEntry(left, width=300, height=35)
        self.entry_name.pack(anchor="w", pady=(5, 20))

        ctk.CTkLabel(left, text="Dates", font=("Arial", 13, "bold"), text_color="gray").pack(anchor="w")
        self.date_start = DateEntry(left, width=12)
        self.date_start.pack(anchor="w", pady=5)
        self.date_end = DateEntry(left, width=12)
        self.date_end.pack(anchor="w", pady=5)

        # DROITE : Compagnons
        right = ctk.CTkFrame(card, fg_color="#222", corner_radius=15)
        right.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(right, text="👥 Gérer les compagnons", font=("Arial", 14, "bold"), text_color="#00aaff").pack(pady=10)
        
        add_row = ctk.CTkFrame(right, fg_color="transparent")
        add_row.pack(fill="x", padx=10)
        self.entry_friend = ctk.CTkEntry(add_row, placeholder_text="Ajouter pseudo...")
        self.entry_friend.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(add_row, text="+", width=40, command=self.add_friend).pack(side="right", padx=5)

        self.list_frame = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, pady=10)

        # Bouton Save (Bas)
        ctk.CTkButton(self, text="💾 Enregistrer tout", command=self.save_all, 
                      fg_color="#e6b800", hover_color="#cfa500", text_color="black", height=50, font=("Arial", 16, "bold")).pack(pady=20, padx=40, fill="x")

    def prefill_data(self):
        self.entry_name.insert(0, self.travel_data['nom_voyage'])
        d1, d2 = self.travel_data['date_depart'], self.travel_data['date_arrivee']
        if isinstance(d1, (datetime, date)): self.date_start.set_date(d1)
        if isinstance(d2, (datetime, date)): self.date_end.set_date(d2)
        self.refresh_list()

    def refresh_list(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        for i, f in enumerate(self.current_friends):
            row = ctk.CTkFrame(self.list_frame, fg_color="#333")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"👤 {f['username']}").pack(side="left", padx=10)
            ctk.CTkButton(row, text="✕", width=25, fg_color="transparent", text_color="red", 
                          command=lambda idx=i: self.remove_friend(idx)).pack(side="right")

    def add_friend(self):
        pseudo = self.entry_friend.get().strip()
        if not pseudo: return
        user = self.crud_user.get_user_by_username(pseudo)
        if not user:
            CTkMessagebox(title="Erreur", message="Utilisateur inconnu", icon="cancel")
            return
        # Eviter doublons
        for f in self.current_friends:
            if f['id_user'] == user['id_user']: return
        
        self.current_friends.append(user)
        self.entry_friend.delete(0, "end")
        self.refresh_list()

    def remove_friend(self, idx):
        del self.current_friends[idx]
        self.refresh_list()

    def save_all(self):
        name = self.entry_name.get().strip()
        d1 = self.date_start.get_date().strftime("%Y-%m-%d")
        d2 = self.date_end.get_date().strftime("%Y-%m-%d")

        try:
            # Update Infos
            self.crud.update_voyage(self.id_voyage, nom_voyage=name, date_depart=d1, date_arrivee=d2)
            
            # Update Amis (Mode bourrin : on supprime tout et on remet, c'est plus simple)
            self.crud_accomp.delete_all_accompagnateurs(self.id_voyage)
            for f in self.current_friends:
                self.crud_accomp.add_accompagnateur(f['id_user'], self.id_voyage)
            
            CTkMessagebox(title="Succès", message="Modifications enregistrées !", icon="check")
            self.master.show_page("ManageTravel")
        except Exception as e:
            CTkMessagebox(title="Erreur", message=str(e), icon="cancel")