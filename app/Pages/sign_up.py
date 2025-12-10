import customtkinter as ctk
from PIL import Image
import re
from CTkMessagebox import CTkMessagebox
from app.backend.crud.users import UsersCRUD

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"

class SignUpPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="#1a1a1a")

        # --- CARTE CENTRALE ---
        self.card = ctk.CTkFrame(self, width=900, height=500, corner_radius=20, fg_color="#2b2b2b")
        self.card.place(relx=0.5, rely=0.5, anchor="center")

        # --- COLONNE GAUCHE (Image) ---
        self.left_frame = ctk.CTkFrame(self.card, width=400, height=500, corner_radius=20, fg_color="#000")
        self.left_frame.pack(side="left", fill="both")
        try:
            img = Image.open('app/Images/Auth_img.png')
            self.img_widget = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 500))
            ctk.CTkLabel(self.left_frame, text="", image=self.img_widget).place(x=0, y=0)
        except:
            ctk.CTkLabel(self.left_frame, text="Rejoignez\nInstravel", font=("Courgette", 30)).place(relx=0.5, rely=0.5, anchor="center")

        # --- COLONNE DROITE (Form) ---
        self.right_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.right_frame.pack(side="right", fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(self.right_frame, text="Créer un compte 🚀", font=("Arial", 28, "bold"), text_color="white").pack(pady=(10, 5))
        ctk.CTkLabel(self.right_frame, text="Commencez à documenter vos aventures.", font=("Arial", 13), text_color="gray").pack(pady=(0, 25))

        # Email
        ctk.CTkLabel(self.right_frame, text="Email", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 2))
        self.entry_mail = ctk.CTkEntry(self.right_frame, width=350, height=35, placeholder_text="email@exemple.com")
        self.entry_mail.pack(pady=(0, 15))

        # Password
        ctk.CTkLabel(self.right_frame, text="Mot de passe", font=("Arial", 13, "bold")).pack(anchor="w", pady=(0, 2))
        self.entry_pass = ctk.CTkEntry(self.right_frame, width=350, height=35, show="*")
        self.entry_pass.pack(pady=(0, 25))

        # Bouton
        self.btn_signup = ctk.CTkButton(
            self.right_frame, text="S'inscrire", command=self.valide_inscription,
            width=350, height=45, fg_color="#2CC985", hover_color="#1e8558", font=("Arial", 15, "bold")
        )
        self.btn_signup.pack()

        # Lien Connexion
        footer = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        footer.pack(pady=20)
        ctk.CTkLabel(footer, text="Déjà un compte ?", font=("Arial", 13)).pack(side="left")
        
        btn_signin = ctk.CTkLabel(footer, text="Se connecter", font=("Arial", 13, "bold"), text_color="#2CC985", cursor="hand2")
        btn_signin.pack(side="left", padx=5)
        btn_signin.bind("<Button-1>", lambda e: self.master.show_page("SignIn"))

    def valide_inscription(self):
        mail = self.entry_mail.get().strip()
        password = self.entry_pass.get().strip()

        if not mail or not password:
            CTkMessagebox(title="Attention", message="Veuillez tout remplir.", icon="warning")
            return

        if not re.match(EMAIL_REGEX, mail):
            CTkMessagebox(title="Erreur", message="Email invalide.", icon="cancel")
            return

        username = mail.split("@")[0]
        crud = UsersCRUD()
        
        try:
            if crud.get_user_by_username(username):
                CTkMessagebox(title="Oups", message="Cet utilisateur existe déjà.", icon="warning")
                return

            crud.create_user(username=username, mail=mail, password=password)
            
            # Succès
            msg = CTkMessagebox(title="Bienvenue !", message="Compte créé avec succès.", icon="check", option_1="Se connecter")
            if msg.get() == "Se connecter":
                self.master.show_page("SignIn")
                
        except Exception as e:
            CTkMessagebox(title="Erreur", message=str(e), icon="cancel")