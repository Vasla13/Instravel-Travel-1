import customtkinter as ctk
# Importez toutes les pages et les CRUDs nécessaires
from app.Pages.home import HomePage
from app.Pages.sign_in import SignInPage
from app.Pages.sign_up import SignUpPage
from app.Pages.view_stage import StageView
from app.Pages.create_stage import CreateStageView
from app.Pages.edit_stage import EditStageView
from app.Pages.create_travel import CreateTravelView
from app.Pages.edit_travel import EditTravelView
from app.Pages.view_travel import ViewTravelView 
from app.Pages.manage_travel import ManageTravelView 
from app.backend.crud.users import UsersCRUD
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.commentaire import CommentairesCRUD
from app.backend.crud.photo import PhotosCRUD
from app.backend.crud.hashtags import HashtagsCRUD
from app.backend.crud.likes import likesCRUD


class Application(ctk.CTk):
    """
    Contrôleur principal gérant la fenêtre, l'état global et la navigation entre les vues (pages).
    """
    def __init__(self):
        super().__init__()
        self.title("InstaTravel")
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.resizable(False, False)

        # Cache des pages : Seules les pages statiques (comme Home, SignIn) sont conservées.
        self.pages = {}
        self.current_page = None

        # --- Initialisation des ressources BDD ---
        self.crud_Voyage = VoyagesCRUD()
        # ID utilisateur actuel (Utilisez un ID valide pour le test, 3 est conservé ici)
        self.current_user_id = 3

        # Démarrage sur la page de gestion
        self.show_page("ManageTravel")

    # ----------------------------------------------------
    # MÉTHODE DE NAVIGATION PRINCIPALE
    # ----------------------------------------------------
    def show_page(self, name, id_item=None):
        """
        Gère l'affichage d'une page. Les pages nécessitant des données fraîches (ManageTravel)
        ou un ID spécifique (EditTravel) sont recréées à chaque fois.
        """
        
        # 1. Cacher la page actuelle
        if self.current_page:
            self.current_page.pack_forget()

        # Pages qui DOIVENT être recréées à chaque appel (pour rafraîchissement ou arguments dynamiques).
        PAGES_RECREATION_REQUIRED = ["ManageTravel", "CreateTravel", "EditTravel", "CreateStage", "EditStage", "StageView"]
        
        # Le rafraîchissement est nécessaire si : le nom est dans la liste OU un argument est passé.
        should_recreate = name in PAGES_RECREATION_REQUIRED or id_item is not None

        # --- Gérer la destruction de l'ancienne instance si on doit recréer ---
        if should_recreate and name in self.pages:
            self.pages[name].destroy()
            del self.pages[name] # Supprime la référence du cache

        # --- Création de la page ---
        if name not in self.pages:
            
            # Pages statiques/semi-statiques
            if name == "SignIn":
                self.pages[name] = SignInPage(self)
            elif name == "SignUp":
                self.pages[name] = SignUpPage(self)
            elif name == "Home":
                self.pages[name] = HomePage(self)

            # Vues dynamiques (Création/Gestion/Édition)
            elif name == "ManageTravel":
                self.pages[name] = ManageTravelView(self, id_user=self.current_user_id)
            
            elif name == "CreateTravel":
                self.pages[name] = CreateTravelView(self, id_user=self.current_user_id)
            
            elif name == "EditTravel":
                if id_item is None: return
                self.pages[name] = EditTravelView(self, id_voyage=id_item)
            
            # --- GESTION DES ÉTAPES ---
            elif name == "CreateStage":
                # id_item contient l'id_voyage
                if id_item is None:
                    print("Erreur: Impossible de créer une étape sans ID de voyage.")
                    return 
                self.pages[name] = CreateStageView(self, id_voyage=id_item)
            
            elif name == "EditStage":
                # id_item contient l'id_etape
                if id_item is None: return
                self.pages[name] = EditStageView(self, etape_id=id_item)
            
            elif name == "StageView":
                # id_item contient l'id_etape
                if id_item is None: return
                self.pages[name] = StageView(self, etape_id=id_item)
        
        # 4. Afficher la page
        if name in self.pages:
            self.current_page = self.pages[name]
            self.current_page.pack(fill="both", expand=True)

    # ----------------------------------------------------
    # GESTION DES VUES DYNAMIQUES PAR ID (Détail/Consultation)
    # ----------------------------------------------------
    def show_travel_detail(self, id_voyage: int):
        """
        Affiche la page de détail d'un voyage (ViewTravelView).
        Recrée toujours la vue pour s'assurer que les données (étapes) sont fraîches.
        """
        
        if self.current_page:
            self.current_page.pack_forget()
            
        # Création et affichage dynamique de ViewTravelView
        # On ne la stocke pas dans self.pages car elle est spécifique à un ID et est recréée
        view = ViewTravelView(self, id_voyage=id_voyage)
        
        self.current_page = view
        self.current_page.pack(fill="both", expand=True)