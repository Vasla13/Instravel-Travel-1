import customtkinter as ctk
from PIL import Image
from typing import List, Optional
import io # Pour lire les blobs d'image
# Importez également UsersCRUD pour charger les noms des accompagnateurs
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.accomp import accompCRUD
from app.backend.crud.users import UsersCRUD 
# Nouveaux imports pour la gestion des étapes
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.photo import PhotosCRUD 
# Pas besoin de get_db ici si les CRUDs le gèrent en interne


# ==== Classe Travel (Modèle inchangé) ====
class Travel:
    """Modèle de données pour les informations d'un voyage (sans dépendance à la BDD)."""
    def __init__(
        self,
        name_of_travel: str,
        beginning_date: str,
        end_date: str,
        escorts: Optional[List[str]] = None
    ):
        self.name_of_travel: str = name_of_travel
        self.beginning_date: str = beginning_date
        self.end_date: str = end_date
        self.escorts: List[str] = escorts if escorts else []

# -------------------------------------------------------------

# ==== Vue du voyage (Mise à jour) ====
class ViewTravelView(ctk.CTkFrame):
    """
    Vue d'affichage d'un voyage avec la liste des étapes.
    """
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent # Référence à l'Application
        self.id_voyage = id_voyage
        self.travel: Optional[Travel] = None
        self.stage_photos_refs = [] # Liste pour garder les références aux objets CTkImage
        
        # Initialisation des CRUDs 
        self.crud_Voyage = VoyagesCRUD()
        self.crud_Accomp = accompCRUD()
        self.crud_Users = UsersCRUD()
        self.crud_Etapes = EtapesCRUD()   # <-- NOUVEAU
        self.crud_Photos = PhotosCRUD()   # <-- NOUVEAU
        
        self.load_travel_data()
        
        if not self.travel:
            ctk.CTkLabel(self, text=f"Erreur: Le voyage {id_voyage} n'existe pas.", text_color="red", font=("Arial", 18, "bold")).pack(pady=50)
            ctk.CTkButton(
                self, 
                text="← Retour à la gestion", 
                command=lambda: self.master.show_page("ManageTravel"),
                width=200, fg_color="#3a3a3a"
            ).pack(pady=20)
            return

        self.setup_ui()
        
    def load_travel_data(self):
        """Récupère les données du voyage et des accompagnateurs depuis la BDD."""
        voyage_data = self.crud_Voyage.get_voyage(self.id_voyage)
        # ... (Logique de chargement des accompagnateurs inchangée) ...
        escorts_names = []
        rows = self.crud_Accomp.get_accompagnateurs_by_voyage(self.id_voyage)
        if rows:
            for row in rows:
                user = self.crud_Users.get_user(row["id_user"])
                if user:
                    escorts_names.append(user["username"])
        
        if voyage_data:
            self.travel = Travel(
                name_of_travel=voyage_data["nom_voyage"],
                beginning_date=voyage_data["date_depart"],
                end_date=voyage_data["date_arrivee"],
                escorts=escorts_names
            )
        else:
            self.travel = None

    def setup_ui(self):
        """Initialise la mise en page de la fenêtre."""
        
        # --- 1. Header Frame (Back Button and Title) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        # Bouton Retour (Flèche)
        ctk.CTkButton(
            header_frame, 
            text="← Retour", 
            command=lambda: self.master.show_page("ManageTravel"),
            width=120, height=35, fg_color="#3a3a3a", hover_color="#505050", font=("Arial", 14, "bold"),
        ).pack(side="left")
        
        # Titre Principal (Nom du Voyage)
        ctk.CTkLabel(
            header_frame, 
            text=self.travel.name_of_travel,
            font=("Courgette", 32, "bold")
        ).pack(side="left", padx=(50, 0), expand=True)

        # --- 2. Scrollable Content Frame ---
        scroll = ctk.CTkScrollableFrame(self, width=780, height=480, fg_color=self.cget("fg_color"))
        scroll.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        
        # Wrapper pour les infos de base (gauche/droite)
        content_wrapper = ctk.CTkFrame(scroll, fg_color="transparent")
        content_wrapper.pack(pady=20, padx=20, fill="x")

        left_frame = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Affichage des informations de base
        self.display_date(left_frame)
        self.display_escorts(right_frame)

        # NOUVELLE SECTION : GESTION DES ÉTAPES
        self.stages_wrapper = ctk.CTkFrame(scroll, fg_color="transparent")
        self.stages_wrapper.pack(fill="x", pady=(0, 20), padx=20)
        self.display_stages_section(self.stages_wrapper)


    # ==== NOUVELLE LOGIQUE D'AFFICHAGE DES ÉTAPES ====

    def display_stages_section(self, parent):
        """Affiche le bouton 'Ajouter Étape' et la liste des étapes."""
        
        stages_frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="#1f1f1f")
        stages_frame.pack(fill="x", pady=10)
        
        header_stages = ctk.CTkFrame(stages_frame, fg_color="transparent")
        header_stages.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(header_stages, text="🗺️ Étapes du Voyage", font=("Arial", 18, "bold"), text_color="#00aaff").pack(side="left")
        
        # Bouton d'ajout d'étape
        ctk.CTkButton(
            header_stages, 
            text="+ Ajouter Étape",
            # On passe l'ID du voyage à la page de création d'étape
            command=lambda: self.master.show_page("CreateStage", id_item=self.id_voyage),
            width=150,
            fg_color="#00aaff"
        ).pack(side="right")

        # Conteneur pour la liste des cartes d'étapes (sera effacé/reconstruit)
        self.stages_container = ctk.CTkFrame(stages_frame, fg_color="transparent")
        self.stages_container.pack(fill="x", padx=15, pady=10)
        
        self.load_and_display_stages()

    def load_and_display_stages(self):
        """Charge les données des étapes et les affiche."""
        
        # Nettoyer
        for widget in self.stages_container.winfo_children():
            widget.destroy()
        self.stage_photos_refs.clear() # Vider les références d'images PIL/CTk

        # 1. Récupérer toutes les étapes pour ce voyage
        etapes = self.crud_Etapes.get_etapes_by_voyage(self.id_voyage)
        
        if not etapes:
            ctk.CTkLabel(self.stages_container, text="Aucune étape n'a encore été ajoutée.", text_color="#bdbdbd").pack(pady=10)
            return

        # 2. Afficher les étapes sous forme de cartes
        for etape in etapes:
            self.create_stage_card(self.stages_container, etape)

    def create_stage_card(self, parent, etape_data: dict):
        """Crée une carte d'aperçu pour une seule étape."""
        
        id_etape = etape_data["id_etape"]
        
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#2b2b2b")
        card.pack(fill="x", pady=5)
        card.grid_columnconfigure(1, weight=1) # Espace pour le texte

        # --- Colonne 0: Aperçu de la Photo ---
        photo_blob = self.crud_Photos.get_first_photo_blob_by_etape(id_etape) # Suppose cette méthode existe
        
        img_label = ctk.CTkLabel(card, text="📸", width=80, height=80, fg_color="#3a3a3a")
        img_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="n")

        if photo_blob:
            try:
                img = Image.open(io.BytesIO(photo_blob))
                img.thumbnail((70, 70))
                photo_tk = ctk.CTkImage(light_image=img, size=(70, 70))
                img_label.configure(image=photo_tk, text="")
                self.stage_photos_refs.append(photo_tk) # Garder la référence!
            except Exception as e:
                img_label.configure(text="Erreur img")

        # --- Colonne 1: Infos Texte ---
        title = etape_data.get("nom_etape", "Sans titre")
        location = etape_data.get("localisation", "Localisation inconnue")
        
        ctk.CTkLabel(
            card, text=title, font=("Arial", 15, "bold")
        ).grid(row=0, column=1, sticky="w", padx=10, pady=(10, 2))
        
        ctk.CTkLabel(
            card, text=f"📍 {location}", font=("Arial", 11), text_color="#bdbdbd"
        ).grid(row=1, column=1, sticky="w", padx=10, pady=(0, 10))


        # --- Colonne 2: Boutons d'Action ---
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=15, pady=10)

        # Bouton Voir Détail
        ctk.CTkButton(
            actions_frame, text="Voir", width=80,
            command=lambda id=id_etape: self.master.show_page("StageView", id_item=id)
        ).pack(pady=3)
        
        # Bouton Modifier
        ctk.CTkButton(
            actions_frame, text="Modifier", width=80, fg_color="orange",
            command=lambda id=id_etape: self.master.show_page("EditStage", id_item=id)
        ).pack(pady=3)
        
        # Bouton Supprimer
        ctk.CTkButton(
            actions_frame, text="Supprimer", width=80, fg_color="red",
            command=lambda id=id_etape: self.confirm_delete_stage(id)
        ).pack(pady=3)


    def confirm_delete_stage(self, id_etape: int):
        """Affiche une boîte de dialogue de confirmation avant la suppression de l'étape."""
        
        msg = CTkMessagebox(
            title="Confirmation de Suppression", 
            message=f"Êtes-vous sûr de vouloir supprimer l'étape ID {id_etape} ?\n\nTous les commentaires et photos associés seront supprimés.",
            icon="question",
            option_1="Annuler",
            option_2="Supprimer"
        )
        response = msg.get()
        
        if response == "Supprimer":
            self.delete_stage(id_etape)

    def delete_stage(self, id_etape: int):
        """Supprime l'étape et toutes ses dépendances (Commentaires, Photos, Hashtags)."""
        # NOTE: Vous devez initialiser CommentairesCRUD, PhotosCRUD, EtapeHashtagCRUD dans ViewTravelView si vous les utilisez ici
        # Pour l'instant, nous faisons appel à une méthode hypothétique de nettoyage dans EtapesCRUD
        
        # La solution la plus simple, si votre EtapesCRUD a été adapté, est de :
        # success = self.crud_Etapes.delete_etape_and_dependencies(id_etape)
        
        # Si vous devez gérer les dépendances manuellement dans la vue (comme pour le voyage)
        try:
            db = get_db()
            # 1. Supprimer les plus petits enfants (Commentaires, Photos, Hashtags)
            self.master.crud_Commentaires.delete_commentaires_by_etape(id_etape) # Supposé exister
            self.master.crud_Photos.delete_photos_for_etape(id_etape)             # Existe dans le CRUD fourni
            # self.master.crud_EtapeHashtag.delete_all_for_etape(id_etape)       # Supposé exister
            
            # 2. Supprimer l'étape parente
            success = self.crud_Etapes.delete_etape(id_etape) # Supposé exister

            if success:
                messagebox.showinfo("Succès", f"Étape {id_etape} supprimée.")
                self.load_and_display_stages() # Rafraîchir l'interface
            else:
                messagebox.showerror("Erreur", "Échec de la suppression de l'étape.")

        except Exception as e:
             messagebox.showerror("Erreur BDD", f"Erreur lors de la suppression de l'étape et des dépendances: {e}")


# ==== Méthodes d'affichage d'informations de base (Inchagées) ====
# ... (display_date et display_escorts) ...

    def display_date(self, parent):
        """Affiche la période du voyage dans un cadre dédié."""
        frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(frame, text="🗓️ Période du voyage", font=("Arial", 16, "bold"), text_color="#00aaff").pack(anchor="w", padx=20, pady=(10, 5))
        
        # Frame interne pour aligner les dates
        date_frame = ctk.CTkFrame(frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        # Départ
        ctk.CTkLabel(date_frame, text="Départ :", font=("Arial", 14, "bold"), text_color="#dcdcdc").pack(side="left", padx=(5, 10))
        ctk.CTkLabel(date_frame, text=self.travel.beginning_date, font=("Arial", 14)).pack(side="left")
        
        # Arrivée
        ctk.CTkLabel(date_frame, text="Arrivée :", font=("Arial", 14, "bold"), text_color="#dcdcdc").pack(side="left", padx=(40, 10))
        ctk.CTkLabel(date_frame, text=self.travel.end_date, font=("Arial", 14)).pack(side="left")

    def display_escorts(self, parent):
        """Affiche les accompagnateurs dans un cadre dédié."""
        frame = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1f1f1f")
        frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(frame, text="👥 Accompagnateurs", font=("Arial", 16, "bold"), text_color="#00aaff").pack(anchor="w", padx=20, pady=(10, 5))
        
        escorts_frame = ctk.CTkFrame(frame, fg_color="transparent")
        escorts_frame.pack(fill="x", padx=15, pady=(0, 10))

        if self.travel.escorts:
            # Affiche la liste des noms, saut de ligne si trop long
            escorts_text = ", ".join(self.travel.escorts)
            ctk.CTkLabel(escorts_frame, text=escorts_text, font=("Arial", 14), text_color="#dcdcdc", wraplength=350, justify="left").pack(anchor="w", padx=5, pady=5)
        else:
            ctk.CTkLabel(escorts_frame, text="Aucun accompagnateur n'a été ajouté.", font=("Arial", 12), text_color="#bdbdbd").pack(anchor="w", padx=5, pady=10)