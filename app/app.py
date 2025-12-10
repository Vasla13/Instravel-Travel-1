import customtkinter as ctk
from tkinter import ttk
# Importez toutes vos pages ici...
from app.Pages.home import HomePage
from app.Pages.sign_in import SignInPage
from app.Pages.sign_up import SignUpPage
from app.Pages.create_stage import CreateStageView
from app.Pages.edit_stage import EditStageView
from app.Pages.create_travel import CreateTravelView
from app.Pages.edit_travel import EditTravelView
from app.Pages.view_travel import ViewTravelView 
from app.Pages.manage_travel import ManageTravelView
from app.Pages.profile import ProfilePage

class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("InstaTravel")
        
        # --- PLEIN ÉCRAN ---
        # Cette commande maximise la fenêtre au démarrage (Windows)
        self.after(0, lambda: self.state('zoomed'))
        self.minsize(1000, 700)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- STYLE DU CALENDRIER (DateEntry) ---
        # Cela change le visuel des calendriers pour qu'ils soient sombres et bleus
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('DateEntry', 
                        fieldbackground='#2b2b2b', 
                        background='#1f6aa5', 
                        foreground='white', 
                        arrowcolor='white')
        
        # Gestion des pages (Cache)
        self.pages = {}
        self.current_page = None
        
        # Gestion Utilisateur
        self.current_user_id = None 
        self.current_user_data = None 

        # Démarrage
        self.show_page("SignIn")

    def login_user(self, user_data: dict):
        self.current_user_data = user_data
        self.current_user_id = user_data['id_user']
        self.show_page("ManageTravel")

    def logout_user(self):
        self.current_user_id = None
        self.current_user_data = None
        self.pages = {} 
        self.show_page("SignIn")

    def show_page(self, name, id_item=None):
        # Sécurité : Si pas connecté, retour au login
        if self.current_user_id is None and name not in ["SignIn", "SignUp"]:
            name = "SignIn"

        if self.current_page:
            self.current_page.pack_forget()

        # Liste des pages qui doivent être rafraîchies à chaque fois
        RECREATE = ["ManageTravel", "Home", "Profile", "CreateTravel", "EditTravel", "CreateStage", "EditStage", "ViewTravel"]
        
        should_recreate = name in RECREATE or id_item is not None

        if should_recreate and name in self.pages:
            self.pages[name].destroy()
            del self.pages[name]

        # Création des pages
        if name not in self.pages:
            if name == "SignIn": self.pages[name] = SignInPage(self)
            elif name == "SignUp": self.pages[name] = SignUpPage(self)
            
            # Pages Connectées
            elif name == "ManageTravel": self.pages[name] = ManageTravelView(self, self.current_user_id)
            elif name == "Home": self.pages[name] = HomePage(self)
            elif name == "Profile": self.pages[name] = ProfilePage(self, self.current_user_id)
            
            elif name == "CreateTravel": self.pages[name] = CreateTravelView(self, self.current_user_id)
            elif name == "EditTravel":
                if id_item: self.pages[name] = EditTravelView(self, id_voyage=id_item)
            
            elif name == "CreateStage":
                if id_item: self.pages[name] = CreateStageView(self, id_voyage=id_item)
            elif name == "EditStage":
                if id_item: self.pages[name] = EditStageView(self, etape_id=id_item)

        # Affichage
        if name in self.pages:
            self.current_page = self.pages[name]
            self.current_page.pack(fill="both", expand=True)

    def show_travel_detail(self, id_voyage: int):
        if self.current_page: self.current_page.pack_forget()
        self.current_page = ViewTravelView(self, id_voyage=id_voyage)
        self.current_page.pack(fill="both", expand=True)