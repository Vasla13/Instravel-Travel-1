import customtkinter as ctk
from PIL import Image
from CTkMessagebox import CTkMessagebox
from app.backend.crud.users import UsersCRUD

class SignInPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        # Image de fond (Optionnel, ici on met une couleur unie propre)
        self.configure(fg_color="#1a1a1a")

        # --- CARTE CENTRALE ---
        # On utilise relx/rely pour centrer parfaitement peu importe la taille de l'écran
        self.card = ctk.CTkFrame(self, width=900, height=500, corner_radius=20, fg_color="#2b2b2b")
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # --- COLONNE GAUCHE : IMAGE ---
        self.left_frame = ctk.CTkFrame(self.card, width=400, height=500, corner_radius=20, fg_color="#000")
        self.left_frame.pack(side="left", fill="both")
        
        try:
            # On essaie de charger une belle image d'accueil
            img = Image.open('app/Images/Auth_img.png')
            # Ajustement de l'image pour remplir le cadre gauche
            self.img_widget = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 500))
            ctk.CTkLabel(self.left_frame, text="", image=self.img_widget).place(x=0, y=0)
        except:
            ctk.CTkLabel(self.left_frame, text="Instravel", font=("Courgette", 40)).place(relx=0.5, rely=0.5, anchor="center")

        # --- COLONNE DROITE : FORMULAIRE ---
        self.right_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        # Logo / Titre
        ctk.CTkLabel(self.right_frame, text="Bon retour ! 👋", font=("Arial", 32, "bold"), text_color="white").pack(pady=(20, 10))
        ctk.CTkLabel(self.right_frame, text="Connectez-vous pour continuer votre voyage.", font=("Arial", 14), text_color="gray").pack(pady=(0, 30))

        # Champ Email
        ctk.CTkLabel(self.right_frame, text="Email", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))
        self.entry_mail = ctk.CTkEntry(self.right_frame, width=350, height=40, placeholder_text="exemple@mail.com")
        self.entry_mail.pack(pady=(0, 20))

        # Champ Password
        ctk.CTkLabel(self.right_frame, text="Mot de passe", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 5))
        self.entry_pass = ctk.CTkEntry(self.right_frame, width=350, height=40, show="*", placeholder_text="••••••••")
        self.entry_pass.pack(pady=(0, 30))

        # Bouton Connexion
        self.btn_login = ctk.CTkButton(
            self.right_frame, text="Se Connecter", command=self.valide_login,
            width=350, height=50, fg_color="#00aaff", hover_color="#0077cc", font=("Arial", 16, "bold")
        )
        self.btn_login.pack()

        # Lien Inscription
        footer = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        footer.pack(pady=20)
        ctk.CTkLabel(footer, text="Pas encore de compte ?", font=("Arial", 13)).pack(side="left")
        
        btn_signup = ctk.CTkLabel(footer, text="Créer un compte", font=("Arial", 13, "bold"), text_color="#00aaff", cursor="hand2")
        btn_signup.pack(side="left", padx=5)
        btn_signup.bind("<Button-1>", lambda e: self.master.show_page("SignUp"))

    def valide_login(self):
        mail = self.entry_mail.get().strip()
        password = self.entry_pass.get().strip()

        if not mail or not password:
            CTkMessagebox(title="Attention", message="Veuillez remplir tous les champs.", icon="warning")
            return

        crud = UsersCRUD()
        user = crud.get_user_by_mail_and_password(mail, password)

        if user:
            # Notification de succès
            CTkMessagebox(title="Succès", message=f"Bienvenue {user['username']} !", icon="check", option_1="C'est parti !")
            self.master.login_user(user)
        else:
            CTkMessagebox(title="Erreur", message="Email ou mot de passe incorrect.", icon="cancel")