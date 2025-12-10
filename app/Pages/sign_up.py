import customtkinter as ctk
from PIL import Image
import re
from CTkMessagebox import CTkMessagebox
from app.backend.crud.users import UsersCRUD

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class SignUpPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # --- Chargement des Images (avec correction du chemin) ---
        try:
            self.logo = ctk.CTkImage(light_image=Image.open('app/Images/Logo.jpg'), size=(300, 150))
            self.logo_set = ctk.CTkLabel(self, text="", image=self.logo)
            self.logo_set.place(x=415, y=-30)

            self.auth_img = ctk.CTkImage(light_image=Image.open('app/Images/Auth_img.png'), size=(320, 569))
            self.auth_img_set = ctk.CTkLabel(self, text="", image=self.auth_img)
            self.auth_img_set.place(x=0, y=0)
        except Exception as e:
            print(f"Attention: Images non trouvées ({e})")

        # --- Formulaire ---
        self.mail = ctk.CTkLabel(self, text="Mail :", font=("Courgette", 20))
        self.mail.place(x=435, y=210)

        self.mail_widget = ctk.CTkEntry(self, width=250)
        self.mail_widget.place(x=435, y=240)

        self.password_txt = ctk.CTkLabel(self, text="Password :", font=("Courgette", 20))
        self.password_txt.place(x=435, y=280)

        self.password_widget = ctk.CTkEntry(self, show="*", width=250)
        self.password_widget.place(x=435, y=310)

        self.login_txt = ctk.CTkLabel(self, text="Inscris-toi pour nous rejoindre !", font=("Courgette", 20))
        self.login_txt.place(x=415, y=150)

        self.inscription_button = ctk.CTkButton(self, width=250, height=40, text="Nous rejoindre !", command=self.valide_inscription)
        self.inscription_button.place(x=435, y=360)

        # --- Liens de redirection ---
        self.page_inscription = ctk.CTkLabel(self, text="Déjà un compte ? ", font=("Courgette", 14))
        self.page_inscription.place(x=335, y=450)

        self.page_connection_redirect = ctk.CTkLabel(self, text="Se connecter", font=("Courgette", 14), text_color="cyan", cursor="hand2")
        self.page_connection_redirect.place(x=450, y=450)

        self.page_connection_redirect.bind("<Enter>", lambda e: self.page_connection_redirect.configure(font=("Courgette", 14, "underline")))
        self.page_connection_redirect.bind("<Leave>", lambda e: self.page_connection_redirect.configure(font=("Courgette", 14)))
        self.page_connection_redirect.bind("<Button-1>", lambda e: self.master.show_page("SignIn"))

    def valide_inscription(self):
        mail = self.mail_widget.get().strip()
        password = self.password_widget.get().strip()

        if not mail or not password:
            CTkMessagebox(title="Erreur", message="Veuillez remplir tous les champs.", icon="warning")
            return

        if not re.match(EMAIL_REGEX, mail):
            CTkMessagebox(title="Erreur", message="Adresse email invalide.", icon="cancel")
            return

        # username = partie avant le @
        username = mail.split("@")[0]

        crud = UsersCRUD()
        try:
            # Vérifier si l'utilisateur existe déjà (optionnel mais conseillé)
            existing = crud.get_user_by_username(username)
            if existing:
                 CTkMessagebox(title="Erreur", message="Ce nom d'utilisateur ou email existe déjà.", icon="cancel")
                 return

            crud.create_user(username=username, mail=mail, password=password)
            
            # Succès : On propose d'aller se connecter
            msg = CTkMessagebox(title="Succès", message="Compte créé avec succès ! Connectez-vous maintenant.", icon="check", option_1="OK")
            if msg.get() == "OK":
                self.master.show_page("SignIn")
                
        except Exception as e:
            CTkMessagebox(title="Erreur Système", message=f"Impossible de créer le compte : {str(e)}", icon="cancel")