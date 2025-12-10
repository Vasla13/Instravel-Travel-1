import customtkinter as ctk
from PIL import Image, ImageDraw, ImageOps

def make_circle(img_path, size=(40, 40)):
    img = Image.open(img_path).resize(size).convert("RGBA")
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    img_round = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    img_round.putalpha(mask)
    return img_round

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Sidebar
        aside = ctk.CTkFrame(self, width=200, height=380, corner_radius=20, fg_color="#353638")
        aside.place(x=0, y=100)

        ctk.CTkLabel(aside, text="PUBLICATIONS", font=("Courgette", 20)).place(x=40, y=10)

        # Logo + profil
        self.logo_img = ctk.CTkImage(light_image=Image.open("Images/Logo.jpg"), size=(200, 100))
        self.logo_label = ctk.CTkLabel(self, text="", image=self.logo_img)
        self.logo_label.place(x=0, y=-20)

        circ_img = make_circle("Images/Auth_img.png", size=(70, 70))
        self.profile_img = ctk.CTkImage(light_image=circ_img, size=(70, 70))
        self.profile_label = ctk.CTkLabel(self, text="", image=self.profile_img)
        self.profile_label.place(x=690, y=5)

        # Barre de recherche
        search_bar = ctk.CTkEntry(self, width=400, height=40, corner_radius=100,
                                  placeholder_text=" Recherchez un '#' ou un nom d'utilisateur !")
        search_bar.place(x=215, y=20)
