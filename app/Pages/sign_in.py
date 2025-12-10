import customtkinter as ctk
from PIL import Image

class SignInPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


        self.logo = ctk.CTkImage(light_image=Image.open('Images/Logo.jpg'),size=(300,150))
        self.logo_set = ctk.CTkLabel(self, text="", image=self.logo)
        self.logo_set.place(x=415, y=-30)

        self.auth_img = ctk.CTkImage(light_image=Image.open('Images/Auth_img.png'),size=(320,569))
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




        self.login_txt = ctk.CTkLabel(self, text="Bienvenue sur notre page de login !", font=("Courgette", 20))
        self.login_txt.place(x=405, y=150)

        self.login_button = ctk.CTkButton(self, width=250, height= 40, text="Connection", command=self.valide_login) # ', command=self.valide_Info)' à ajouter ici lorsque prêt
        self.login_button.place(x=435, y=360)

        self.page_inscription = ctk.CTkLabel(self, text="Pas encore membre ? ", font=("Courgette", 14))
        self.page_inscription.place(x=335, y=450)

        self.page_inscription_redirect = ctk.CTkLabel(self, text="S'inscrire", font=("Courgette", 14),text_color="cyan", cursor="hand2")
        self.page_inscription_redirect.place(x=475, y=450)

        self.page_inscription_redirect.bind("<Enter>", lambda e: self.page_inscription_redirect.configure(font=("Courgette", 14, "underline")))
        self.page_inscription_redirect.bind("<Leave>", lambda e: self.page_inscription_redirect.configure(font=("Courgette", 14)))
        self.page_inscription_redirect.bind("<Button-1>", lambda e: self.master.show_page("SignUp"))


        

    def valide_login(self):
        mail = self.mail_widget.get().strip()
        password = self.password_widget.get().strip()
        if self.label is not None:
            self.label.destroy()
            self.label=None

        if not mail or not password:
            self.label=customtkinter.CTkLabel(self, text="⚠️ Remplis tous les champs", text_color="orange")
            self.label.place(x=435, y=400)
            return

        crud = UsersCRUD()
        user = crud.get_user_by_mail_and_password(mail, password)

        if user:
            self.master.current_user = user  # on stocke l’utilisateur dans la fenêtre principale
            self.label=customtkinter.CTkLabel(self, text=f"✅ Bienvenue {user['username']} !", text_color="green")
            self.label.place(x=435, y=400)
            # Ici tu peux rediriger vers une nouvelle page, ex: page d'accueil
            # self.master.show_page("homepage")
        else:
            self.label = customtkinter.CTkLabel(self, text="❌ Identifiants invalides", text_color="red")
            self.label.place(x=435, y=400)