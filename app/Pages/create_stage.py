import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import filedialog
from PIL import Image, ImageTk
import io
from CTkMessagebox import CTkMessagebox
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.photo import PhotosCRUD

class CreateStageView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        self.crud = EtapesCRUD()
        self.crud_photo = PhotosCRUD()
        
        # Données photo
        self.selected_photo_bytes = None
        
        # Liste Villes Optimisée
        self.villes_opti = [
            "Paris, France", "Marseille, France", "Lyon, France", 
            "Londres, UK", "New York, USA", "Tokyo, Japon", 
            "Rome, Italie", "Barcelone, Espagne", "Berlin, Allemagne", 
            "Sydney, Australie", "Dubai, UAE", "Rio de Janeiro, Brésil",
            "Amsterdam, Pays-Bas", "Lisbonne, Portugal", "Bangkok, Thaïlande",
            "Los Angeles, USA", "San Francisco, USA", "Miami, USA",
            "Montréal, Canada", "Marrakech, Maroc", "Istanbul, Turquie"
        ]

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(header, text="← Retour", command=lambda: self.master.show_travel_detail(self.id_voyage), 
                      fg_color="#444", width=100).pack(side="left")
        ctk.CTkLabel(header, text="✨ Nouvelle Étape", font=("Courgette", 28, "bold"), text_color="#00aaff").pack(side="left", padx=30)

        # Scroll
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Card
        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=15)
        card.pack(fill="x", padx=10, pady=10)

        # --- GAUCHE : Formulaire ---
        left_side = ctk.CTkFrame(card, fg_color="transparent")
        left_side.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(left_side, text="Titre de l'étape *", font=("Arial", 14, "bold"), text_color="#ccc").pack(anchor="w", pady=(0, 5))
        self.entry_nom = ctk.CTkEntry(left_side, width=300, height=35)
        self.entry_nom.pack(anchor="w")

        # Date & Lieu
        ctk.CTkLabel(left_side, text="Date", font=("Arial", 13, "bold"), text_color="#ccc").pack(anchor="w", pady=(15,5))
        self.entry_date = DateEntry(left_side, date_pattern="dd/mm/yyyy", width=12, background='darkblue', foreground='white', borderwidth=2)
        self.entry_date.pack(anchor="w")

        ctk.CTkLabel(left_side, text="Lieu (Auto-complétion)", font=("Arial", 13, "bold"), text_color="#ccc").pack(anchor="w", pady=(15,5))
        self.entry_lieu = ctk.CTkComboBox(left_side, width=300, height=35, values=self.villes_opti)
        self.entry_lieu.set("") 
        self.entry_lieu.pack(anchor="w")

        # --- DROITE : Zone Photo ---
        right_side = ctk.CTkFrame(card, fg_color="#222", corner_radius=15)
        right_side.pack(side="right", padx=20, pady=20, anchor="n")
        
        self.lbl_preview = ctk.CTkLabel(right_side, text="Aucune photo\nsélectionnée", width=200, height=150, fg_color="#333", corner_radius=10)
        self.lbl_preview.pack(padx=10, pady=10)

        ctk.CTkButton(right_side, text="📷 Choisir une photo", command=self.choose_photo, fg_color="#3b8ed0").pack(pady=(0,10), padx=10)

        # Description (En bas, pleine largeur)
        ctk.CTkLabel(left_side, text="Description", font=("Arial", 13, "bold"), text_color="#ccc").pack(anchor="w", pady=(15, 5))
        self.entry_desc = ctk.CTkTextbox(left_side, width=400, height=100, corner_radius=10)
        self.entry_desc.pack(anchor="w", fill="x")

        # BOUTON VALIDER
        self.btn_save = ctk.CTkButton(
            self.scroll, text="✅  Enregistrer l'étape", command=self.save_stage, 
            fg_color="#2CC985", hover_color="#229A65", height=50, font=("Arial", 16, "bold")
        )
        self.btn_save.pack(pady=20, padx=40, fill="x")

    def choose_photo(self):
        """Ouvre l'explorateur et redimensionne l'image."""
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                # 1. Ouvrir et Redimensionner (Optimisation)
                img = Image.open(file_path)
                img.thumbnail((400, 400)) # Max 400px
                
                # 2. Convertir pour affichage (Preview)
                preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 130))
                self.lbl_preview.configure(image=preview_img, text="")
                
                # 3. Convertir en binaire pour SQL
                output = io.BytesIO()
                img.save(output, format="PNG") # On normalise en PNG
                self.selected_photo_bytes = output.getvalue()
                
            except Exception as e:
                CTkMessagebox(title="Erreur Image", message=f"Impossible de lire l'image: {e}", icon="cancel")

    def save_stage(self):
        nom = self.entry_nom.get().strip()
        lieu = self.entry_lieu.get().strip()
        desc = self.entry_desc.get("1.0", "end").strip()
        date_obj = self.entry_date.get_date()
        date_sql = date_obj.strftime("%Y-%m-%d")

        if not nom:
            CTkMessagebox(title="Erreur", message="Titre obligatoire", icon="warning")
            return

        try:
            # 1. Créer l'étape
            id_etape = self.crud.create_etape(self.id_voyage, nom, date_sql, desc, lieu)
            
            # 2. Sauvegarder la photo si présente
            if self.selected_photo_bytes:
                self.crud_photo.add_photo(id_etape, self.selected_photo_bytes)
                
            self.master.show_travel_detail(self.id_voyage)
        except Exception as e:
            CTkMessagebox(title="Erreur", message=str(e), icon="cancel")