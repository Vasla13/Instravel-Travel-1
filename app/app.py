import customtkinter as ctk
# Importez toutes les pages
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

class Application(ctk.CTk):
    """
    Contrôleur principal gérant la fenêtre, l'état global et la navigation.
    """
    def __init__(self):
        super().__init__()
        self.title("InstaTravel")
        self.geometry("800x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.resizable(False, False)

        # Cache des pages
        self.pages = {}
        self.current_page = None

        # --- GESTION UTILISATEUR ---
        # Plus d'ID forcé à 3. On démarre à None.
        self.current_user_id = None 
        self.current_user_data = None # Pour stocker username, email, etc.

        # Démarrage sur la page de connexion
        self.show_page("SignIn")

    def login_user(self, user_data: dict):
        """Connecte l'utilisateur et débloque l'accès à l'app."""
        self.current_user_data = user_data
        self.current_user_id = user_data['id_user']
        print(f"Utilisateur connecté : {user_data['username']} (ID: {self.current_user_id})")
        # Redirection vers la gestion des voyages
        self.show_page("ManageTravel")

    def logout_user(self):
        """Déconnecte l'utilisateur."""
        self.current_user_id = None
        self.current_user_data = None
        self.pages = {} # Vider le cache pour sécurité
        self.show_page("SignIn")

    def show_page(self, name, id_item=None):
        """Gère la navigation."""
        
        # Protection : Si on n'est pas connecté et qu'on veut aller ailleurs que SignIn/SignUp/Home
        if self.current_user_id is None and name not in ["SignIn", "SignUp", "Home"]:
            print("Accès refusé. Redirection vers SignIn.")
            name = "SignIn"

        # 1. Cacher la page actuelle
        if self.current_page:
            self.current_page.pack_forget()

        # Pages qui DOIVENT être recréées à chaque appel
        PAGES_RECREATION_REQUIRED = ["ManageTravel", "CreateTravel", "EditTravel", "CreateStage", "EditStage", "StageView"]
        should_recreate = name in PAGES_RECREATION_REQUIRED or id_item is not None

        if should_recreate and name in self.pages:
            self.pages[name].destroy()
            del self.pages[name]

        # --- Création de la page ---
        if name not in self.pages:
            
            if name == "SignIn":
                self.pages[name] = SignInPage(self)
            elif name == "SignUp":
                self.pages[name] = SignUpPage(self)
            elif name == "Home":
                self.pages[name] = HomePage(self)

            # Vues nécessitant un utilisateur connecté
            elif name == "ManageTravel":
                self.pages[name] = ManageTravelView(self, id_user=self.current_user_id)
            
            elif name == "CreateTravel":
                self.pages[name] = CreateTravelView(self, id_user=self.current_user_id)
            
            elif name == "EditTravel":
                if id_item is None: return
                self.pages[name] = EditTravelView(self, id_voyage=id_item)
            
            elif name == "CreateStage":
                if id_item is None: return 
                self.pages[name] = CreateStageView(self, id_voyage=id_item)
            
            elif name == "EditStage":
                if id_item is None: return
                self.pages[name] = EditStageView(self, etape_id=id_item)
            
            elif name == "StageView":
                if id_item is None: return
                self.pages[name] = StageView(self, etape_id=id_item)
        
        # Afficher la page
        if name in self.pages:
            self.current_page = self.pages[name]
            self.current_page.pack(fill="both", expand=True)

    def show_travel_detail(self, id_voyage: int):
        if self.current_page:
            self.current_page.pack_forget()
        view = ViewTravelView(self, id_voyage=id_voyage)
        self.current_page = view
        self.current_page.pack(fill="both", expand=True)