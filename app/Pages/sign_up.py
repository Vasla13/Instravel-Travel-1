import customtkinter as ctk
from PIL import Image
import re
from app.backend.crud.users import UsersCRUD

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


class SignUpPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.logo = ctk.CTkImage(light_image=Image.open('Images/Logo.jpg'), size=(300, 150))
        self.logo_set = ctk.CTkLabel(self, text="", image=self.logo)
        self.logo_set.place(x=415, y=-30)

        self.auth_img = ctk.CTkImage(light_image=Image.open('Images/Auth_img.png'), size=(320, 569))
        self.auth_img_set = ctk.CTkLabel(self, text="", image=self.auth_img)
        self.auth_img_set.place(x=0, y=0)

        self.mail = ctk.CTkLabel(self, text="Mail :", font=("Courgette", 20))
        self.mail.place(x=435, y=210)

        self.mail_widget = ctk.CTkEntry(self, width=250)
        self.mail_widget.place(x=435, y=240)

        self.password_txt = ctk.CTkLabel(self, text="Password :", font=("Courgette", 20))
        self.password_txt.place(x=435, y=280)

        self.password_widget = ctk.CTkEntry(self, show="*", width=250)
        self.password_widget.place(x=435, y=310)

        self.login_txt = ctk.CTkLabel(self, text="Inscrit toi pour nous rejoindre !", font=("Courgette", 20))
        self.login_txt.place(x=425, y=150)

        self.inscription_button = ctk.CTkButton(self, width=250, height=40, text="Nous rejoindre !", command=self.valide_inscription)
        self.inscription_button.place(x=435, y=360)

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
            ctk.CTkLabel(self, text="⚠️ Remplis tous les champs", text_color="orange").place(x=435, y=360)
            return

        if not re.match(EMAIL_REGEX, mail):
            ctk.CTkLabel(self, text="❌ Adresse email invalide", text_color="red").place(x=435, y=360)
            return

        # username = partie avant le @
        username = mail.split("@")[0]

        crud = UsersCRUD()
        try:
            crud.create_user(username=username, mail=mail, password=password)
            ctk.CTkLabel(self, text="✅ Compte créé avec succès !", text_color="green").place(x=435, y=360)
        except Exception as e:
            ctk.CTkLabel(self, text=f"❌ Erreur : {str(e)}", text_color="red").place(x=435, y=360)

    