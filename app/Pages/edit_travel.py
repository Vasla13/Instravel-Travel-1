import customtkinter as ctk
# Importez la classe pour les boîtes de dialogue de confirmation 
from CTkMessagebox import CTkMessagebox 
from tkinter.constants import END 
# Importez DateEntry pour le sélecteur de date
from tkcalendar import DateEntry 
import tkinter as tk 
import datetime # Importé pour la gestion des objets date
from typing import List, Optional

from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.accomp import accompCRUD
from app.backend.crud.users import UsersCRUD

# Importez la classe Application pour la navigation
try:
    from app.app import Application
except ImportError:
    class Application: pass 


class EditTravelView(ctk.CTkFrame):
    """Page d'édition de voyage avec gestion des accompagnateurs et protection contre les pertes de données."""

    def __init__(self, parent: Application, id_voyage: int = 1):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage

        # Initialisation des CRUD
        self.crud_Voyage = VoyagesCRUD()
        self.crud_Accomp = accompCRUD()
        self.crud_Users = UsersCRUD()
        
        self.escorts = [] 
        self.is_dirty = False 

        # 1. Récupération des données initiales du voyage
        voyage_data = self.crud_Voyage.get_voyage(id_voyage)
        if not voyage_data:
            raise ValueError(f"Le voyage {id_voyage} n'existe pas !")

        self.travel_name = voyage_data["nom_voyage"]
        # Les dates peuvent être des objets datetime.date ou des chaînes selon la configuration du connecteur MySQL
        self.date_depart = voyage_data["date_depart"]
        self.date_arrivee = voyage_data["date_arrivee"]

        # 2. Chargement initial des accompagnateurs
        self.load_escorts()

        # 3. Construction de l'interface utilisateur
        self.setup_ui()

    # NOUVELLE MÉTHODE: Marquer l'état comme "modifié"
    def mark_as_dirty(self, *args):
        """Définit l'état de la vue comme 'modifié' lorsqu'un champ est touché."""
        self.is_dirty = True

    # NOUVELLE MÉTHODE: Vérification avant de quitter
    def check_unsaved_changes(self):
        """Vérifie si des modifications ont été effectuées et demande confirmation avant de quitter."""
        if self.is_dirty:
            msg = CTkMessagebox(
                title="Modifications non enregistrées", 
                message="Vous avez des modifications non enregistrées. Voulez-vous abandonner ces changements ?",
                icon="warning",
                option_1="Non",
                option_2="Abandonner"
            )
            response = msg.get()
            
            if response == "Abandonner":
                self.is_dirty = False 
                self.master.show_page("ManageTravel")
            
        else:
            self.master.show_page("ManageTravel")


    def setup_ui(self):
        """Initialise la mise en page de la fenêtre avec le style amélioré."""
        
        # --- 1. Header Frame (Back Button and Title) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        # Bouton Retour (MODIFIÉ pour appeler la vérification)
        ctk.CTkButton(
            header_frame, 
            text="← Retour", 
            command=self.check_unsaved_changes, 
            width=120,
            height=35,
            fg_color="#3a3a3a", 
            hover_color="#505050",
            font=("Arial", 14, "bold"),
        ).pack(side="left")
        
        # Titre Principal
        ctk.CTkLabel(
            header_frame, 
            text=f"Modifier : {self.travel_name}",
            font=("Courgette", 32, "bold")
        ).pack(side="left", padx=(50, 0), expand=True)

        # --- 2. Scrollable Content Frame ---
        self.scroll = ctk.CTkScrollableFrame(self, width=780, height=480, fg_color=self.cget("fg_color"))
        self.scroll.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        self.display_name_dates_section()
        self.display_escorts_section()
        self.display_save_button()
        
    # ================= Sections d'affichage =================
    
    def display_name_dates_section(self):
        """Affiche les champs pour le nom et les dates du voyage (avec sélecteurs de calendrier)."""
        frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(frame, text="✏️ Détails du Voyage", font=("Arial", 16, "bold"), text_color="#00aaff").pack(anchor="w", padx=15, pady=(10, 5))

        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=5)

        # Nom du voyage
        ctk.CTkLabel(content_frame, text="Nom du Voyage", font=("Arial", 13, "bold")).pack(anchor="w", padx=15, pady=(5, 5))
        self.name_entry = ctk.CTkEntry(content_frame, width=300)
        self.name_entry.insert(0, self.travel_name)
        self.name_entry.bind('<KeyRelease>', self.mark_as_dirty) 
        self.name_entry.pack(anchor="w", padx=15, pady=(0, 10))

        # Dates
        date_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        # --- DATE DE DÉPART ---
        depart_label_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        depart_label_frame.pack(side="left", padx=(0, 30))
        
        ctk.CTkLabel(depart_label_frame, text="Départ", font=("Arial", 13, "bold")).pack(anchor="w")
        
        depart_entry_frame = ctk.CTkFrame(depart_label_frame, fg_color="transparent")
        depart_entry_frame.pack(anchor="w")
        
        # Utilisation de tkcalendar.DateEntry
        self.date_depart_entry = DateEntry(
            depart_entry_frame, 
            date_pattern='dd/mm/yyyy',
            width=15, 
            bordercolor="#00aaff", 
            foreground='white',
            selectbackground="#00aaff",
            normalbackground="#2b2b2b",
        )
        # Chargement de la date initiale depuis la BDD
        if self.date_depart:
            if isinstance(self.date_depart, str):
                try:
                    # Si c'est une chaîne, conversion en objet date
                    initial_date = datetime.datetime.strptime(self.date_depart, '%Y-%m-%d').date()
                    self.date_depart_entry.set_date(initial_date)
                except ValueError:
                    pass
            elif isinstance(self.date_depart, (datetime.date, datetime.datetime)):
                # Si c'est déjà un objet date, l'utiliser directement
                self.date_depart_entry.set_date(self.date_depart)
        
        self.date_depart_entry.bind("<<DateEntrySelected>>", self.mark_as_dirty) 
        self.date_depart_entry.pack(side="left")

        # --- DATE D'ARRIVÉE ---
        arrivee_label_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        arrivee_label_frame.pack(side="left")
        
        ctk.CTkLabel(arrivee_label_frame, text="Arrivée", font=("Arial", 13, "bold")).pack(anchor="w")
        
        arrivee_entry_frame = ctk.CTkFrame(arrivee_label_frame, fg_color="transparent")
        arrivee_entry_frame.pack(anchor="w")
        
        # Utilisation de tkcalendar.DateEntry
        self.date_arrivee_entry = DateEntry(
            arrivee_entry_frame, 
            date_pattern='dd/mm/yyyy',
            width=15, 
            bordercolor="#00aaff", 
            foreground='white',
            selectbackground="#00aaff",
            normalbackground="#2b2b2b",
        )
        # Chargement de la date initiale depuis la BDD
        if self.date_arrivee:
            if isinstance(self.date_arrivee, str):
                try:
                    initial_date = datetime.datetime.strptime(self.date_arrivee, '%Y-%m-%d').date()
                    self.date_arrivee_entry.set_date(initial_date)
                except ValueError:
                    pass
            elif isinstance(self.date_arrivee, (datetime.date, datetime.datetime)):
                self.date_arrivee_entry.set_date(self.date_arrivee)

        self.date_arrivee_entry.bind("<<DateEntrySelected>>", self.mark_as_dirty)
        self.date_arrivee_entry.pack(side="left")
        
    def display_escorts_section(self):
        """Affiche le formulaire d'ajout et la liste des accompagnateurs."""
        frame = ctk.CTkFrame(self.scroll, corner_radius=15, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=20)

        ctk.CTkLabel(frame, text="👥 Gérer les Accompagnateurs", font=("Arial", 16, "bold"), text_color="#00aaff").pack(anchor="w", padx=15, pady=(10, 5))

        # Entrée et bouton Ajouter
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=5)
        self.escort_entry = ctk.CTkEntry(top_frame, width=250, placeholder_text="Nom accompagnateur")
        self.escort_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(top_frame, text="Ajouter", command=self.add_escort, width=100, fg_color="#00aaff", hover_color="#0088cc").pack(side="left")

        # Conteneur pour la liste (sera rempli par display_escorts)
        self.accomp_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.accomp_container.pack(fill="both", padx=15, pady=10)
        self.display_escorts() # Affichage initial

    def display_save_button(self):
        """Affiche le bouton de sauvegarde."""
        ctk.CTkButton(
            self.scroll, 
            text="💾 Sauvegarder les Modifications", 
            height=40, 
            command=self.save_travel,
            font=("Arial", 16, "bold"),
            fg_color="#00aaff", hover_color="#0088cc"
        ).pack(pady=20)

    # ================= Logique BDD et Affichage =================

    def load_escorts(self):
        """Charge la liste des accompagnateurs depuis la DB dans self.escorts."""
        self.escorts = []
        rows = self.crud_Accomp.get_accompagnateurs_by_voyage(self.id_voyage)
        
        if rows:
            for row in rows:
                user = self.crud_Users.get_user(row["id_user"]) 
                if user:
                    self.escorts.append({"id_user": row["id_user"], "username": user["username"]})
    
    def display_escorts(self):
        """Met à jour l'affichage de la liste des accompagnateurs."""
        for w in self.accomp_container.winfo_children():
            w.destroy()

        # Reconstruire la liste
        for i, acc in enumerate(self.escorts):
            card = ctk.CTkFrame(self.accomp_container, corner_radius=10, fg_color="#2b2b2b")
            card.pack(fill="x", padx=5, pady=5)
            ctk.CTkLabel(card, text=acc["username"], font=("Arial", 13, "bold")).pack(side="left", padx=10, pady=10)
            
            ctk.CTkButton(
                card, text="Supprimer", width=80, fg_color="red", hover_color="darkred",
                command=lambda idx=i: self.delete_escort(idx)
            ).pack(side="right", padx=10, pady=10)

    def add_escort(self):
        """Ajoute un accompagnateur au voyage après vérification."""
        name = self.escort_entry.get().strip()
        if not name:
            return

        user = self.crud_Users.get_user_by_username(name)
        if user is None:
            print(f"L'utilisateur '{name}' n'existe pas !")
            return

        id_user = user["id_user"]

        self.load_escorts()
        if any(a["id_user"] == id_user for a in self.escorts):
            print(f"L'utilisateur '{name}' est déjà ajouté au voyage !")
            return

        self.crud_Accomp.create_accompagnateur(id_user=id_user, id_voyage=self.id_voyage)
        
        self.load_escorts()
        self.display_escorts()
        self.escort_entry.delete(0, 'end')
        
        self.is_dirty = True 

    def delete_escort(self, index: int):
        """Supprime un accompagnateur du voyage et rafraîchit l'affichage."""
        if 0 <= index < len(self.escorts):
            id_user = self.escorts[index]["id_user"]
            
            self.crud_Accomp.db.cursor.execute(
                "DELETE FROM accomp WHERE id_user=%s AND id_voyage=%s",
                (id_user, self.id_voyage)
            )
            self.crud_Accomp.db.commit()
            
            self.load_escorts()
            self.display_escorts()
            
            self.is_dirty = True 

    def save_travel(self):
        self.travel_name = self.name_entry.get().strip()
        
        # Récupération des objets date de DateEntry
        depart_date_obj = self.date_depart_entry.get_date()
        arrivee_date_obj = self.date_arrivee_entry.get_date()
        
        # Formatage en 'YYYY-MM-DD' pour la BDD (gestion des dates None)
        self.date_depart = depart_date_obj.strftime("%Y-%m-%d") if depart_date_obj else None
        self.date_arrivee = arrivee_date_obj.strftime("%Y-%m-%d") if arrivee_date_obj else None

        # Appel au CRUD pour la mise à jour
        self.crud_Voyage.update_voyage(
            id_voyage=self.id_voyage,
            nom_voyage=self.travel_name,
            date_depart=self.date_depart,
            date_arrivee=self.date_arrivee
        )
        print(f"Voyage '{self.travel_name}' (ID: {self.id_voyage}) mis à jour !")
        
        # RÉINITIALISER L'ÉTAT après sauvegarde
        self.is_dirty = False