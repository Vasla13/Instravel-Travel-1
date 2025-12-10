import customtkinter as ctk
from tkcalendar import DateEntry
from typing import List, Optional
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.accomp import accompCRUD
from app.backend.crud.users import UsersCRUD
# Import pour la vérification de l'ID utilisateur
from CTkMessagebox import CTkMessagebox 

class Travel:
    """Classe représentant un voyage."""
    def __init__(self, name: str = "", start_date: str = "", end_date: str = "",
                 escorts: Optional[List[str]] = None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.escorts = escorts if escorts else []

class CreateTravelView(ctk.CTkFrame):
    """Page CTkFrame pour créer un voyage (sans gestion d'étapes)."""
    
    def __init__(self, parent, id_user: int = None): 
        super().__init__(parent)
        self.master = parent # Stocker la référence à l'Application
        self.id_user = id_user

        # CRUD
        self.crud_Voyage = VoyagesCRUD()
        self.crud_Accomp = accompCRUD()
        self.crud_Users = UsersCRUD()
        
        # NOTE : Gestion de l'utilisateur non défini
        if self.id_user is None or self.id_user == 0:
             self.global_error_label = ctk.CTkLabel(self, text="ERREUR: Utilisateur non défini ou non connecté.", text_color="red", font=("Arial", 14, "bold"))
             self.global_error_label.pack(pady=50)
             return
             
        self.travel = Travel()
        self.escorts: List[str] = []

        # Label d'erreur global
        self.global_error_label = ctk.CTkLabel(self, text="", text_color="red", font=("Arial", 14, "bold"))
        self.global_error_label.pack(pady=(5,0))

        # Construction de l'interface
        self.setup_ui()

        # Après création, on stockera l'id_voyage
        self.id_voyage: Optional[int] = None

    def setup_ui(self):
        """Initialise la mise en page de la fenêtre (Header + Scroll)."""
        
        # --- 1. Header Frame (Bouton Retour + Titre) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        # Bouton Retour
        ctk.CTkButton(
            header_frame, 
            text="← Retour", 
            command=lambda: self.master.show_page("ManageTravel"),
            width=120,
            height=35,
            fg_color="#3a3a3a", 
            hover_color="#505050",
            font=("Arial", 14, "bold"),
        ).pack(side="left")
        
        # Titre Principal
        ctk.CTkLabel(
            header_frame, 
            text="Création d'un Voyage",
            font=("Courgette", 32, "bold")
        ).pack(side="left", padx=(50, 0), expand=True)

        # --- 2. Scroll principal ---
        self.scroll = ctk.CTkScrollableFrame(self, width=780, height=450, fg_color=self.cget("fg_color"))
        self.scroll.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Sections
        self.display_name()
        self.display_dates()
        self.display_escorts()
        self.display_create_button()


    # ================== Sections ==================
    def display_name(self):
        """Affiche le champ pour le nom du voyage."""
        frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(frame, text="Nom du Voyage", font=("Arial", 15, "bold")).pack(anchor="w", padx=15, pady=(10,5))
        self.name_entry = ctk.CTkEntry(frame, width=400, placeholder_text="Nom du Voyage")
        self.name_entry.pack(anchor="w", padx=15, pady=(0,5))
        self.name_error = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
        self.name_error.pack(anchor="w", padx=15, pady=(0,10))

    def display_dates(self):
        """Affiche les sélecteurs de date (DateEntry)."""
        frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(frame, text="Dates du Voyage", font=("Arial", 15, "bold")).pack(anchor="w", padx=15, pady=(10,5))
        
        date_wrapper = ctk.CTkFrame(frame, fg_color="transparent")
        date_wrapper.pack(anchor="w", padx=15, pady=5)
        
        # Date de début
        ctk.CTkLabel(date_wrapper, text="Début:", font=("Arial", 13, "bold")).pack(side="left", padx=(0,5))
        self.date_debut = DateEntry(date_wrapper, date_pattern="dd/mm/yyyy", width=15)
        self.date_debut.pack(side="left", padx=(0,15), pady=5)
        
        # Date de fin
        ctk.CTkLabel(date_wrapper, text="Fin:", font=("Arial", 13, "bold")).pack(side="left", padx=(5,5))
        self.date_fin = DateEntry(date_wrapper, date_pattern="dd/mm/yyyy", width=15)
        self.date_fin.pack(side="left", padx=5, pady=5)
        
        self.date_error = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
        self.date_error.pack(anchor="w", padx=15, pady=(0,10))

    def display_escorts(self):
        """Affiche le champ d'ajout et la liste des accompagnateurs."""
        frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=20)
        ctk.CTkLabel(frame, text="Accompagnateurs", font=("Arial", 15, "bold")).pack(anchor="w", padx=15, pady=(10,5))
        top_acc = ctk.CTkFrame(frame, fg_color="transparent")
        top_acc.pack(fill="x", padx=10, pady=5)
        self.escort_entry = ctk.CTkEntry(top_acc, width=250, placeholder_text="Nom de l'accompagnateur")
        self.escort_entry.pack(side="left", padx=(0,10))
        ctk.CTkButton(top_acc, text="Ajouter", command=self.add_escort, fg_color="#00aaff", hover_color="#0088cc").pack(side="left")
        self.badges_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.badges_container.pack(fill="x", padx=10, pady=5)
        self.escort_error = ctk.CTkLabel(frame, text="", text_color="red", font=("Arial", 12))
        self.escort_error.pack(anchor="w", padx=15, pady=(0,10))

    def display_create_button(self):
        ctk.CTkButton(self.scroll, text="Créer le Voyage", command=self.create_travel, height=40, font=("Arial", 16, "bold")).pack(pady=20)

    # ================== Méthodes ==================
    def add_escort(self):
        # ... (méthode add_escort)
        name = self.escort_entry.get().strip()
        if not name: return
        if len(self.escorts) >= 8:
            self.escort_error.configure(text="* Maximum 8 accompagnateurs")
            return
        
        # Vérification si l'utilisateur existe avant d'ajouter le badge (bonne pratique)
        user = self.crud_Users.get_user_by_username(name.strip().lower())
        if not user:
            self.escort_error.configure(text=f"* L'utilisateur '{name}' n'existe pas.")
            return

        self.escorts.append(name) 
        self.escort_entry.delete(0,"end")
        self.display_escorts_list()
        self.escort_error.configure(text="")

    def display_escorts_list(self):
        # ... (méthode display_escorts_list)
        for w in self.badges_container.winfo_children(): w.destroy()
        for i, acc in enumerate(self.escorts):
            card = ctk.CTkFrame(self.badges_container, corner_radius=10, fg_color="#2b2b2b")
            card.pack(fill="x", pady=3, padx=10)
            ctk.CTkLabel(card, text=acc, font=("Arial", 12)).pack(side="left", padx=10, pady=5)
            ctk.CTkButton(card, text="✕", width=26, height=26, fg_color="red", hover_color="darkred",
                          corner_radius=13, command=lambda idx=i: self.delete_escort(idx)).pack(side="right", padx=10, pady=5)

    def delete_escort(self, idx):
        # ... (méthode delete_escort)
        if 0 <= idx < len(self.escorts):
            self.escorts.pop(idx)
            self.display_escorts_list()

    def create_travel(self):
        valid = True
        self.global_error_label.configure(text="")

        name = self.name_entry.get().strip()
        if not name:
            self.name_error.configure(text="* Nom obligatoire")
            valid = False
        else: self.name_error.configure(text="")

        # Récupération des objets date (DateEntry)
        start = self.date_debut.get_date()
        end = self.date_fin.get_date()
        
        # Vérification des dates
        if start >= end:
            self.date_error.configure(text="* Date début doit être avant date fin")
            valid = False
        else: self.date_error.configure(text="")

        if not valid:
            self.global_error_label.configure(text="Veuillez corriger les erreurs")
            return
            
        # VÉRIFICATION CRUCIALE : Assurez-vous que l'ID utilisateur est valide
        if not self.crud_Users.get_user(self.id_user):
             self.global_error_label.configure(text="ERREUR: L'ID utilisateur est invalide. Vérifiez la connexion.", text_color="red")
             return

        self.travel.name = name
        # Le format YYYY-MM-DD est nécessaire pour MySQL
        self.travel.start_date = start.strftime("%Y-%m-%d")
        self.travel.end_date = end.strftime("%Y-%m-%d")
        self.travel.escorts = self.escorts

        # Création BDD
        try:
            voyage_id = self.crud_Voyage.create_voyage(
                id_user=self.id_user,
                nom_voyage=self.travel.name,
                date_depart=self.travel.start_date,
                date_arrivee=self.travel.end_date
            )
            self.id_voyage = voyage_id
        except Exception as e:
            self.global_error_label.configure(text=f"Erreur BDD lors de la création du voyage: {e}", text_color="red")
            return

        # Ajout des accompagnateurs
        for escort in self.escorts:
            user = self.crud_Users.get_user_by_username(escort.strip().lower())
            if user:
                try:
                    self.crud_Accomp.create_accompagnateur(user["id_user"], voyage_id)
                except Exception as e:
                    print(f"Erreur lors de l'ajout de l'accompagnateur {escort}: {e}")

        # --- NOUVELLE LOGIQUE DE REDIRECTION ---
        self.global_error_label.configure(text=f"Voyage créé avec succès ! ID={voyage_id} (Redirection dans 5 secondes)", text_color="green")
        print(f"Voyage créé en BDD avec id={voyage_id}. Redirection imminente.")
        
        # Redirection après 5 secondes
        self.master.after(5000, lambda: self.master.show_page("ManageTravel"))
        # ----------------------------------------