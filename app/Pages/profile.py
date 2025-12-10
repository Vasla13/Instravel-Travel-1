import customtkinter as ctk
from PIL import Image
import io
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from app.backend.crud.users import UsersCRUD

class ProfilePage(ctk.CTkFrame):
    def __init__(self, parent, id_user: int):
        super().__init__(parent)
        self.master = parent
        self.id_user = id_user
        self.crud = UsersCRUD()
        
        self.user_data = self.crud.get_user(id_user)
        self.new_photo_bytes = None
        
        self.setup_ui()

    def setup_ui(self):
        # --- NAVBAR (Navigation Commune) ---
        nav = ctk.CTkFrame(self, height=60, fg_color="#111", corner_radius=0)
        nav.pack(fill="x", side="top")
        
        ctk.CTkButton(nav, text="🏠 Mes Voyages", command=lambda: self.master.show_page("ManageTravel"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=10)
        
        ctk.CTkButton(nav, text="🌍 Explorer", command=lambda: self.master.show_page("Home"), 
                      fg_color="transparent", hover_color="#333", width=120).pack(side="left", padx=5)

        ctk.CTkButton(nav, text="👤 Mon Profil", fg_color="#333", width=120).pack(side="left", padx=5) # Actif
        
        ctk.CTkButton(nav, text="Déconnexion", command=self.master.logout_user, 
                      fg_color="#cf3030", hover_color="#a01010", width=100).pack(side="right", padx=20, pady=10)

        # --- CONTENU ---
        content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Carte Profil
        card = ctk.CTkFrame(content, fg_color="#2b2b2b", corner_radius=20)
        card.pack(pady=20, padx=100, fill="both")

        # Header: Photo & Pseudo
        top_sec = ctk.CTkFrame(card, fg_color="transparent")
        top_sec.pack(fill="x", padx=40, pady=40)

        # 1. Photo de profil
        self.avatar_frame = ctk.CTkFrame(top_sec, width=150, height=150, corner_radius=75, fg_color="#444")
        self.avatar_frame.pack(side="left")
        self.avatar_frame.pack_propagate(False)
        
        self.load_current_avatar()

        # Bouton changer photo
        ctk.CTkButton(top_sec, text="📷 Changer", width=80, command=self.choose_photo, fg_color="#444", hover_color="#555").pack(side="left", anchor="s", padx=10)

        # 2. Infos Texte
        info_box = ctk.CTkFrame(top_sec, fg_color="transparent")
        info_box.pack(side="left", padx=40, fill="x", expand=True)

        ctk.CTkLabel(info_box, text=f"@{self.user_data['username']}", font=("Arial", 32, "bold"), text_color="white", anchor="w").pack(fill="x")
        ctk.CTkLabel(info_box, text=self.user_data['mail'], font=("Arial", 14), text_color="gray", anchor="w").pack(fill="x")

        # Formulaire Modifiable
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=40, pady=(0, 40))

        # Bio
        ctk.CTkLabel(form, text="Ma Biographie", font=("Arial", 14, "bold"), text_color="#ccc").pack(anchor="w", pady=(20, 5))
        self.entry_bio = ctk.CTkTextbox(form, height=100, corner_radius=10, font=("Arial", 14), fg_color="#1a1a1a")
        self.entry_bio.pack(fill="x")
        if self.user_data['biographie']:
            self.entry_bio.insert("1.0", self.user_data['biographie'])

        # Nationalité
        ctk.CTkLabel(form, text="Nationalité / Ville", font=("Arial", 14, "bold"), text_color="#ccc").pack(anchor="w", pady=(20, 5))
        self.entry_nat = ctk.CTkEntry(form, height=40, font=("Arial", 14), fg_color="#1a1a1a")
        self.entry_nat.pack(fill="x")
        if self.user_data['nationalite']:
            self.entry_nat.insert(0, self.user_data['nationalite'])

        # Bouton Sauvegarder
        ctk.CTkButton(form, text="💾 Enregistrer les modifications", command=self.save_profile, 
                      height=50, font=("Arial", 16, "bold"), fg_color="#00aaff", hover_color="#0088cc").pack(pady=40, fill="x")

    def load_current_avatar(self):
        # Affichage photo actuelle ou placeholder
        if self.user_data['photo']:
            try:
                img = Image.open(io.BytesIO(self.user_data['photo']))
                ctk_img = ctk.CTkImage(img, size=(150, 150))
                self.lbl_ava = ctk.CTkLabel(self.avatar_frame, text="", image=ctk_img)
                self.lbl_ava.place(x=0, y=0)
            except: pass
        else:
            ctk.CTkLabel(self.avatar_frame, text="👤", font=("Arial", 60)).place(relx=0.5, rely=0.5, anchor="center")

    def choose_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            try:
                img = Image.open(path)
                img.thumbnail((300, 300))
                
                # Preview
                ctk_img = ctk.CTkImage(img, size=(150, 150))
                self.lbl_ava = ctk.CTkLabel(self.avatar_frame, text="", image=ctk_img)
                self.lbl_ava.place(x=0, y=0)
                
                # Save bytes
                out = io.BytesIO()
                img.save(out, format="PNG")
                self.new_photo_bytes = out.getvalue()
            except Exception as e:
                CTkMessagebox(title="Erreur", message=f"Image invalide: {e}", icon="cancel")

    def save_profile(self):
        bio = self.entry_bio.get("1.0", "end").strip()
        nat = self.entry_nat.get().strip()
        
        # Préparation des données à mettre à jour
        # Note: UsersCRUD.update_user attend 'photo' comme bytes ou str selon implémentation.
        # Ici on suppose qu'il accepte les bytes ou qu'on doit adapter CRUD.
        # Si update_user dans votre code attend str, on va devoir le modifier légèrement.
        # Pour l'instant on envoie.
        
        try:
            self.crud.update_user(
                self.id_user,
                biographie=bio,
                nationalite=nat,
                photo=self.new_photo_bytes if self.new_photo_bytes else None
            )
            CTkMessagebox(title="Succès", message="Profil mis à jour !", icon="check")
        except Exception as e:
            CTkMessagebox(title="Erreur", message=f"Erreur BDD: {e}", icon="cancel")