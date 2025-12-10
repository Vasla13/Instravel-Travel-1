import customtkinter as ctk
from datetime import datetime
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD

class ManageTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_user: int = None):
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        self.crud = VoyagesCRUD()

        # --- Header (Titre + Bouton Ajouter) ---
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=20)

        self.title = ctk.CTkLabel(
            self.header, 
            text="✈️ Mes Aventures", 
            font=("Courgette", 32, "bold"),
            text_color="#00aaff"
        )
        self.title.pack(side="left")

        self.btn_add = ctk.CTkButton(
            self.header, 
            text="+ Nouveau Voyage", 
            font=("Arial", 14, "bold"),
            fg_color="#2CC985", 
            hover_color="#229A65",
            height=40,
            command=lambda: self.master.show_page("CreateTravel")
        )
        self.btn_add.pack(side="right")

        # --- Zone de liste (Scrollable) ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Chargement des données
        self.load_travels()

    def load_travels(self):
        """Récupère les voyages et génère les cartes."""
        # Nettoyer l'affichage précédent
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Récupérer les données BDD
        try:
            voyages = self.crud.get_voyages_by_user(self.id_user)
        except Exception as e:
            ctk.CTkLabel(self.scroll_frame, text=f"Erreur de connexion BDD: {e}", text_color="red").pack()
            return

        if not voyages:
            self.show_empty_state()
        else:
            for v in voyages:
                self.create_travel_card(v)

    def show_empty_state(self):
        """Affiche un message si aucun voyage."""
        container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        container.pack(pady=50)
        ctk.CTkLabel(container, text="📭", font=("Arial", 60)).pack()
        ctk.CTkLabel(container, text="Aucun voyage pour l'instant.", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(container, text="Cliquez sur '+ Nouveau Voyage' pour commencer !", text_color="gray").pack()

    def create_travel_card(self, voyage):
        """Crée une jolie carte pour un voyage."""
        # Cadre de la carte
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=15, fg_color="#2b2b2b", border_width=1, border_color="#3a3a3a")
        card.pack(fill="x", padx=10, pady=8)

        # --- Colonne Gauche : Infos ---
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", padx=15, pady=15, fill="both", expand=True)

        # Titre
        ctk.CTkLabel(info_frame, text=voyage['nom_voyage'], font=("Arial", 18, "bold"), anchor="w").pack(fill="x")
        
        # Dates (Formatage joli)
        d_start = voyage['date_depart'] # C'est un objet date ou str selon le connecteur
        d_end = voyage['date_arrivee']
        
        # Gestion sécurité format date
        date_str = "Dates inconnues"
        if d_start and d_end:
            try:
                # Si c'est déjà un objet date python
                s = d_start.strftime("%d/%m/%Y") if hasattr(d_start, 'strftime') else str(d_start)
                e = d_end.strftime("%d/%m/%Y") if hasattr(d_end, 'strftime') else str(d_end)
                date_str = f"📅 Du {s} au {e}"
            except:
                date_str = f"📅 {d_start} - {d_end}"

        ctk.CTkLabel(info_frame, text=date_str, font=("Arial", 14), text_color="#aaaaaa", anchor="w").pack(fill="x", pady=(5,0))

        # --- Colonne Droite : Actions ---
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=15, pady=15)

        # Bouton Voir
        ctk.CTkButton(
            action_frame, text="Voir", width=80, 
            fg_color="#3b8ed0", hover_color="#36719f",
            command=lambda: self.master.show_travel_detail(voyage['id_voyage'])
        ).pack(side="left", padx=5)

        # Bouton Modifier
        ctk.CTkButton(
            action_frame, text="✏️", width=40, 
            fg_color="#e6b800", hover_color="#cc9900", text_color="black",
            command=lambda: self.master.show_page("EditTravel", id_item=voyage['id_voyage'])
        ).pack(side="left", padx=5)

        # Bouton Supprimer
        ctk.CTkButton(
            action_frame, text="🗑️", width=40, 
            fg_color="#ff4d4d", hover_color="#cc0000",
            command=lambda: self.confirm_delete(voyage)
        ).pack(side="left", padx=5)

    def confirm_delete(self, voyage):
        """Demande confirmation avant suppression."""
        msg = CTkMessagebox(
            title="Supprimer ?", 
            message=f"Voulez-vous vraiment supprimer le voyage '{voyage['nom_voyage']}' ?\nCela supprimera aussi les étapes et photos associées.",
            icon="warning", 
            option_1="Annuler", 
            option_2="Supprimer"
        )
        
        if msg.get() == "Supprimer":
            if self.crud.delete_voyage(voyage['id_voyage']):
                self.load_travels() # Recharger la liste
                CTkMessagebox(title="Succès", message="Voyage supprimé.", icon="check")
            else:
                CTkMessagebox(title="Erreur", message="Impossible de supprimer le voyage.", icon="cancel")