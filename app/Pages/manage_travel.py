import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
# Importez les CRUDs nécessaires pour la gestion des dépendances
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.accomp import accompCRUD
from app.backend.crud.commentaire import CommentairesCRUD
from app.backend.crud.hashtags import HashtagsCRUD
from app.backend.crud.photo import PhotosCRUD

# Importez le module app.app pour la référence à la classe Application
try:
    from app.app import Application
except ImportError:
    class Application: pass 

class ManageTravelView(ctk.CTkFrame):
    """Page de gestion affichant tous les voyages de l'utilisateur avec actions (Voir, Modifier, Supprimer)."""

    def __init__(self, parent: Application, id_user: int):
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        
        # Initialisation des CRUDs pour la suppression en cascade
        self.crud_Voyage = VoyagesCRUD()
        self.crud_Etapes = EtapesCRUD()
        self.crud_Accomp = accompCRUD()
        self.crud_Commentaire = CommentairesCRUD()
        self.crud_Hashtags = HashtagsCRUD()
        self.crud_Photos = PhotosCRUD()
        
        self.setup_ui()
        # L'appel initial est fait ici
        self.load_and_display_travels() 

    def setup_ui(self):
        """Initialisation des éléments UI de base."""
        
        # --- Cadre de Défilement (Scrollable Frame) ---
        self.scroll = ctk.CTkScrollableFrame(self, width=780, height=580)
        self.scroll.pack(padx=10, pady=10, fill="both", expand=True)

        # --- En-tête et Bouton Créer (Séparé du conteneur de voyages) ---
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 5), padx=10)
        
        # Titre
        ctk.CTkLabel(header_frame, text="Gérer Mes Voyages", font=("Courgette", 28)).pack(side="left", padx=(10, 0))
        
        # Bouton Créer un Nouveau Voyage
        ctk.CTkButton(
            header_frame, 
            text="+ Créer un Nouveau Voyage", 
            command=lambda: self.master.show_page("CreateTravel"),
            width=200,
            height=35,
            fg_color="#00aaff",
            hover_color="#0088cc",
            font=("Arial", 14, "bold")
        ).pack(side="right", padx=10)

        # Conteneur pour les cartes de voyage (C'est ce qui sera nettoyé et redessiné)
        self.travel_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.travel_container.pack(fill="x", padx=10, pady=5)
        
    # NOUVELLE MÉTHODE : Permet de rafraîchir la vue de l'extérieur (appelé par Application après création)
    def refresh_view(self):
        """Déclenche le rechargement et l'affichage des voyages."""
        self.load_and_display_travels()

    def load_and_display_travels(self):
        """Charge les voyages de l'utilisateur et met à jour l'affichage."""
        
        # Nettoyer le conteneur avant de recharger
        for widget in self.travel_container.winfo_children():
            widget.destroy()

        # Récupération des données filtrées par utilisateur
        travels = self.crud_Voyage.get_voyages_by_user(self.id_user)
        
        if not travels:
            ctk.CTkLabel(self.travel_container, text="Vous n'avez créé aucun voyage pour l'instant.", text_color="#bdbdbd").pack(pady=20)
            return

        for travel in travels:
            self.create_travel_card(self.travel_container, travel)

    def create_travel_card(self, parent, travel_data: dict):
        """Crée une carte affichant les détails et les boutons d'action d'un voyage."""
        card = ctk.CTkFrame(parent, corner_radius=15, fg_color="#2b2b2b")
        card.pack(fill="x", padx=5, pady=5)
        
        travel_id = travel_data["id_voyage"]
        nom = travel_data["nom_voyage"]
        dates = f"Du {travel_data['date_depart']} au {travel_data['date_arrivee']}"

        # Gauche: Nom et Dates
        text_frame = ctk.CTkFrame(card, fg_color="transparent")
        text_frame.pack(side="left", padx=15, pady=10, anchor="w")
        
        ctk.CTkLabel(text_frame, text=nom, font=("Arial", 15, "bold")).pack(anchor="w")
        ctk.CTkLabel(text_frame, text=dates, font=("Arial", 11), text_color="#b0b0b0").pack(anchor="w")

        # Droite: Boutons d'Action
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(side="right", padx=15, pady=10)

        # Bouton Voir (View)
        ctk.CTkButton(
            action_frame, text="Voir", width=80,
            command=lambda id=travel_id: self.master.show_travel_detail(id)
        ).pack(side="left", padx=5)

        # Bouton Modifier (Edit)
        ctk.CTkButton(
            action_frame, text="Modifier", width=80, fg_color="orange", hover_color="#cc8800",
            command=lambda id=travel_id: self.master.show_page("EditTravel", id)
        ).pack(side="left", padx=5)

        # Bouton Supprimer (Delete)
        ctk.CTkButton(
            action_frame, text="Supprimer", width=80, fg_color="red", hover_color="darkred",
            command=lambda id=travel_id, name=nom: self.confirm_delete(id, name)
        ).pack(side="left", padx=5)

    def confirm_delete(self, id_voyage: int, nom_voyage: str):
        """Affiche une boîte de dialogue de confirmation avant la suppression."""
        
        msg = CTkMessagebox(
            title="Confirmation de Suppression", 
            message=f"Êtes-vous sûr de vouloir supprimer le voyage '{nom_voyage}' (ID: {id_voyage}) ?\n\nTOUTES les données associées (étapes, commentaires, photos, etc.) seront supprimées.",
            icon="question",
            option_1="Annuler",
            option_2="Supprimer Définitivement",
            width=500
        )
        response = msg.get()
        
        if response == "Supprimer Définitivement":
            self.delete_travel(id_voyage)

    def delete_travel(self, id_voyage: int):
        """
        Supprime un voyage et toutes ses dépendances.
        """
        
        try:
            # 1. Supprimer les relations de jointure les plus profondes (Hashtags)
            self.crud_Hashtags.delete_etape_hashtags_by_voyage(id_voyage) 
            
            # 2. Supprimer les COMMENTAIRES
            self.crud_Commentaire.delete_commentaires_by_voyage(id_voyage)
            
            # 3. Supprimer les PHOTOS
            self.crud_Photos.delete_photos_by_voyage(id_voyage)

            # 4. Supprimer les relations de jointure directes du VOYAGE (Accompagnateurs)
            self.crud_Accomp.delete_accomp_by_voyage(id_voyage) 
            
            # 5. Supprimer les ETAPES (qui n'ont plus d'enfants)
            self.crud_Etapes.delete_etapes_by_voyage(id_voyage) 

            # 6. Supprimer le VOYAGE (le grand-parent)
            success = self.crud_Voyage.delete_voyage(id_voyage)
            
            if success:
                print(f"Voyage {id_voyage} et dépendances supprimés avec succès.")
                self.load_and_display_travels() # Recharger la liste
            else:
                CTkMessagebox(title="Erreur", message="Échec: Le voyage n'a pas pu être supprimé de la table voyages.", icon="cancel")
                
        except Exception as e:
            print(f"Erreur fatale lors de la suppression du voyage {id_voyage}: {e}")
            CTkMessagebox(title="Erreur BDD", 
                          message=f"Une erreur s'est produite lors du nettoyage des dépendances. Erreur : {e}", 
                          icon="cancel")