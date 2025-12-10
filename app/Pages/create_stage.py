import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox
import io
from datetime import date, datetime
import re
from typing import List, Optional

# Import des CRUDs et de la base de données
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.etape_hashtag import EtapeHashtagCRUD
from app.backend.crud.photo import PhotosCRUD
from app.backend.database import get_db
from app.backend.crud.hashtags import HashtagsCRUD
from tkcalendar import DateEntry


# ==================== UTILS ====================

def format_date_for_mysql(date_str: str) -> str:
    """
    Convertit une date JJ/MM/AAAA en AAAA-MM-JJ pour MySQL.
    Retourne la chaîne vide si invalide.
    """
    if not date_str:
        return ""
    match = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", date_str)
    if not match:
        return ""
    day, month, year = match.groups()
    try:
        d = datetime(int(year), int(month), int(day))
        return d.strftime("%Y-%m-%d")
    except ValueError:
        return ""

class CreateStageView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int, *args, **kwargs): 
        super().__init__(parent, *args, **kwargs)
        self.master = parent # Référence à l'Application
        self.id_voyage = id_voyage # ID du voyage parent
        
        self.selected_photos = []
        self.hashtags = [] 
        self.MAX_HASHTAG_LEN = 10
        
        # --- LAYOUT CORRIGÉ : Utiliser uniquement PACK ---
        self.pack(fill="both", expand=True)
        self.pack_propagate(False)
        
        self.setup_ui()


    def setup_ui(self):
        """Initialise la structure UI : Header et Scrollable Content."""
        
        # --- 1. Header (Bouton Retour + Titre) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 5))

        # Bouton Retour (revient à la vue du voyage)
        ctk.CTkButton(
            header_frame, 
            text="← Retour au Voyage", 
            command=lambda: self.master.show_travel_detail(self.id_voyage),
            width=150, height=35, fg_color="#3a3a3a", hover_color="#505050",
        ).pack(side="left")
        
        ctk.CTkLabel(
            header_frame, 
            text="Création d'une Étape",
            font=("Courgette", 32, "bold")
        ).pack(side="left", padx=20)
        
        # --- 2. Cadre Scrollable Principal ---
        self.main_scroll = ctk.CTkScrollableFrame(self, width=760, height=420)
        self.main_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # === Conteneur principal pour les deux colonnes (à l'intérieur du scroll) ===
        main_content_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        main_content_frame.pack(fill="x", pady=10, padx=10)
        
        # Colonnes pour les champs (utilisent désormais PACK SIDE)
        self.left_main_column = ctk.CTkFrame(main_content_frame, fg_color="#1f1f1f")
        self.left_main_column.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=10)
        
        self.right_main_column = ctk.CTkFrame(main_content_frame, fg_color="#1f1f1f")
        self.right_main_column.pack(side="right", fill="both", expand=True, padx=(5, 0), pady=10)
        
        # Initialisation des sections
        self.display_left_inputs()
        self.display_right_inputs()
        self.display_publish_button()


    def display_left_inputs(self):
        """Contient les champs Titre, Description, Localisation, Date, Hashtags."""
        left_main_column = self.left_main_column

        ctk.CTkLabel(left_main_column, text="Informations principales", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 15))
        
        # Titre de l'étape
        ctk.CTkLabel(left_main_column, text="Titre de l'étape *").pack(anchor="w", padx=10, pady=(2, 0))
        self.title_entry = ctk.CTkEntry(left_main_column, width=320, placeholder_text="Ex: Visite de la Tour Eiffel")
        self.title_entry.pack(anchor="w", padx=10, pady=(2, 5))
        
        # Description
        ctk.CTkLabel(left_main_column, text="Description *").pack(anchor="w", padx=10, pady=(2, 0))
        self.description_text = ctk.CTkTextbox(left_main_column, width=320, height=80) 
        self.description_text.pack(anchor="w", padx=10, pady=(2, 5))
        
        # Localisation
        ctk.CTkLabel(left_main_column, text="Localisation *").pack(anchor="w", padx=10, pady=(2, 0))
        self.location_entry = ctk.CTkEntry(left_main_column, width=320, placeholder_text="Ex: Paris, France")
        self.location_entry.pack(anchor="w", padx=10, pady=(2, 5))
        
        # Date
        ctk.CTkLabel(left_main_column, text="Date *").pack(anchor="w", padx=10, pady=(2, 0))
        date_container = ctk.CTkFrame(left_main_column, width=150, height=28)
        date_container.pack_propagate(False)
        date_container.pack(anchor="w", padx=10, pady=(2, 5))
        self.date_picker = DateEntry(master=date_container, state="readonly", date_pattern="dd/MM/yyyy", locale="fr_FR")
        self.date_picker.config(width=12)
        self.date_picker.pack(fill="both", expand=True)

        # Hashtags
        hashtag_header = ctk.CTkFrame(left_main_column, fg_color="transparent")
        hashtag_header.pack(fill="x", padx=10, pady=(5, 5))
        ctk.CTkLabel(hashtag_header, text="Hashtags").pack(side="left")
        hashtag_row = ctk.CTkFrame(left_main_column, fg_color="transparent")
        hashtag_row.pack(anchor="w", padx=10, pady=(0, 6))
        self.hashtag_input = ctk.CTkEntry(hashtag_row, width=240, placeholder_text="Maximum 3 # et 10 caractères")
        self.hashtag_input.pack(side="left")
        self.add_hashtag_btn = ctk.CTkButton(hashtag_row, text="+", width=28, command=self.add_hashtag)
        self.add_hashtag_btn.pack(side="left", padx=(8, 0))
        self.hashtag_input.bind("<Return>", lambda e: self.add_hashtag())
        self.hashtags_container = ctk.CTkFrame(left_main_column, fg_color="transparent")
        self.hashtags_container.pack(anchor="w", padx=10, pady=(0, 10))
        self.refresh_hashtags_view()

    def display_right_inputs(self):
        """Contient les boutons Photos et l'Aperçu."""
        right_main_column = self.right_main_column
        
        ctk.CTkLabel(right_main_column, text="Photos *", 
                     font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(10, 15))
        
        # Boutons pour gérer les photos
        photo_buttons_frame = ctk.CTkFrame(right_main_column, fg_color="transparent")
        photo_buttons_frame.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.add_photo_btn = ctk.CTkButton(photo_buttons_frame, text="📷 Ajouter", command=self.add_photos, width=100)
        self.add_photo_btn.pack(side="left", padx=(0, 5))
        
        self.clear_photos_btn = ctk.CTkButton(photo_buttons_frame, text="🗑️ Effacer", command=self.clear_photos, width=80)
        self.clear_photos_btn.pack(side="left")
        
        # Zone d'aperçu des photos
        self.photos_preview_frame = ctk.CTkFrame(right_main_column, height=260, width=350, fg_color="transparent")
        self.photos_preview_frame.pack(fill="y", expand=True, padx=10, pady=(0, 5))
        self.photos_preview_frame.pack_propagate(False)
        
        self.photos_info_label = ctk.CTkLabel(self.photos_preview_frame, text="Minimum 1 photo requise")
        self.photos_info_label.pack(pady=20)
        self.update_photos_preview()

    def display_publish_button(self):
        """Affiche les boutons d'action (Publier/Annuler)."""
        buttons_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        buttons_frame.pack(pady=(10, 20), padx=10)
        
        self.publish_btn = ctk.CTkButton(buttons_frame, text="📤 Publier", 
                                         command=self.publish_stage, width=120, height=35, 
                                         fg_color="#00aaff", hover_color="#0088cc")
        self.publish_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ctk.CTkButton(buttons_frame, text="❌ Annuler", 
                                        command=self.cancel_creation, width=100, height=35)
        self.cancel_btn.pack(side="left")
        
    
    # --- METHODES DE TRAITEMENT ---
    
    def add_photos(self):
        """Ouvre un dialogue pour sélectionner des photos"""
        remaining_slots = 6 - len(self.selected_photos)
        if remaining_slots <= 0:
            messagebox.showwarning("Limite atteinte", "Vous ne pouvez sélectionner que 6 photos maximum.")
            return
        
        file_types = [
            ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Tous les fichiers", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title=f"Sélectionner des photos (max {remaining_slots} restantes)",
            filetypes=file_types
        )
        
        if files:
            files_to_add = list(files)[:remaining_slots]
            if len(files) > remaining_slots:
                messagebox.showinfo("Limite de photos", 
                                     f"Seules les {remaining_slots} premières photos ont été ajoutées (limite de 6 photos).")
            
            self.selected_photos.extend(files_to_add)
            self.update_photos_preview()
    
    def clear_photos(self):
        """Supprime toutes les photos sélectionnées"""
        self.selected_photos.clear()
        self.update_photos_preview()
    
    def update_photos_preview(self):
        """Met à jour l'aperçu des photos sélectionnées"""
        for widget in self.photos_preview_frame.winfo_children():
            if widget != self.photos_info_label:
                widget.destroy()
        
        if not self.selected_photos:
            self.photos_info_label.configure(text="Minimum 1 photo requise")
            self.photos_info_label.pack(pady=20)
        else:
            self.photos_info_label.pack_forget()
            
            thumbnails_container = ctk.CTkFrame(self.photos_preview_frame, fg_color="transparent")
            thumbnails_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            num_photos = len(self.selected_photos)
            thumbnails_grid = ctk.CTkFrame(thumbnails_container, fg_color="transparent")
            thumbnails_grid.pack(expand=True, padx=5, pady=5)
            
            for col in range(min(3, num_photos)):
                thumbnails_grid.grid_columnconfigure(col, weight=1, minsize=105)
            
            for i, photo_data in enumerate(self.selected_photos):
                try:
                    img = Image.open(photo_data)
                    img.thumbnail((90, 90))
                    
                    photo_frame = ctk.CTkFrame(thumbnails_grid, width=105, height=115)
                    photo_frame.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="nsew")
                    photo_frame.grid_propagate(False)
                    
                    photo_tk = ctk.CTkImage(light_image=img, size=(90, 90))
                    img_label = ctk.CTkLabel(photo_frame, image=photo_tk, text="")
                    img_label.image = photo_tk  # garde une ref
                    img_label.pack(pady=(3, 1))
                    
                    remove_btn = ctk.CTkButton(photo_frame, text="✕", width=18, height=18,
                                               command=lambda idx=i: self.remove_photo(idx),
                                               font=("Arial", 9))
                    remove_btn.pack(pady=(0, 3))
                    
                except Exception as e:
                    print(f"Erreur lors du chargement de {photo_data}: {e}")
            
            counter_label = ctk.CTkLabel(thumbnails_container, 
                                        text=f"{num_photos}/6 photos", 
                                        font=("Arial", 10))
            counter_label.pack(pady=(5, 0))

    def remove_photo(self, idx):
        """Supprime une photo sélectionnée"""
        self.selected_photos.pop(idx)
        self.update_photos_preview()
        
    def get_stage_data(self):
        """Récupère les données saisies dans le formulaire"""
        hashtags = self.hashtags.copy()
        
        selected_date = self.date_picker.get_date()
        date_str = selected_date.strftime("%d/%m/%Y") if selected_date else ""
        date_sql = format_date_for_mysql(date_str)
        
        return {
            "title": self.title_entry.get().strip(),
            "description": self.description_text.get("1.0", "end-1c").strip(),
            "location": self.location_entry.get().strip(),
            "date": date_sql,
            "photos": self.selected_photos.copy(),
            "hashtags": hashtags
        }
    
    def validate_data(self, data):
        """Valide les données saisies"""
        errors = []
        
        if not data["title"]: errors.append("Le titre est obligatoire")
        if not data["description"]: errors.append("La description est obligatoire")
        if not data["location"]: errors.append("La localisation est obligatoire")
        if not data["date"]: errors.append("La date est obligatoire")
        if not data["photos"] or len(data["photos"]) == 0: errors.append("Au moins une photo est obligatoire")
            
        # Validation des hashtags 
        if "hashtags" in data:
            if len(data["hashtags"]) > 3: errors.append("Maximum 3 hashtags autorisés")
            for tag in data["hashtags"]:
                if not tag.startswith('#'): errors.append(f"Le hashtag '{tag}' doit commencer par un #")
                if len(tag) < 2: errors.append("Un hashtag doit contenir au moins un caractère après le #")
                if ' ' in tag: errors.append(f"Les espaces ne sont pas autorisés dans les hashtags: '{tag}'")
                if len(tag[1:]) > self.MAX_HASHTAG_LEN: errors.append(f"Le hashtag '{tag}' dépasse {self.MAX_HASHTAG_LEN} caractères")
        
        return errors
    
    def publish_stage(self):
        """Publie l'étape dans la base de données"""
        data = self.get_stage_data()
        errors = self.validate_data(data)

        if errors:
            error_message = "Erreurs de validation :\n" + "\n".join(f"• {error}" for error in errors)
            messagebox.showerror("Erreurs de validation", error_message)
            return

        try:
            db = get_db()
            etapes_crud = EtapesCRUD(db)
            hashtags_crud = EtapeHashtagCRUD(db)
            tags_crud = HashtagsCRUD(db)
            photos_crud = PhotosCRUD(db)
            id_voyage = self.id_voyage

            # Création de l'étape
            id_etape = etapes_crud.create_etape(
                nom_etape=data["title"],
                date_etape=data["date"],
                description=data["description"],
                localisation=data["location"], 
                nb_commentaire=0,
                nb_like=0,
                id_voyage=id_voyage,
            )

            # Gestion des hashtags (déduplication avec set) via CRUD
            for tag in set(data["hashtags"]):
                id_hashtag = tags_crud.get_or_create(tag)
                hashtags_crud.add_hashtag_to_etape(id_etape, id_hashtag)

            # Envoi des photos en binaire dans la base de données
            for photo_data in data["photos"]:
                with open(photo_data, "rb") as photo_file:
                    photo_bytes = photo_file.read()
                photos_crud.create_photo(photo_bytes, id_etape)

            db.commit()
            messagebox.showinfo("Succès", "Étape publiée avec succès !")

            # Redirection vers la vue du voyage après succès (pour voir la nouvelle étape)
            self.master.show_travel_detail(id_voyage)

        except Exception as e:
            # CORRECTION ROLLBACK 
            try:
                if hasattr(db.cursor, 'connection') and db.cursor.connection:
                    db.cursor.connection.rollback()
            except Exception as rollback_e:
                print(f"Erreur lors du rollback (ignorée): {rollback_e}")

            messagebox.showerror("Erreur", f"Impossible d'enregistrer l'étape : {e}")

    
    def cancel_creation(self):
        """Annule la création de l'étape et revient à la vue du voyage."""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir annuler la création de l'étape ?"):
             self.clear_all()
             self.master.show_travel_detail(self.id_voyage) # Retourne au voyage parent
             
    def clear_all(self):
        """Efface tous les champs du formulaire"""
        if not self.selected_photos or messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir effacer tous les champs ?"):
            self.title_entry.delete(0, "end")
            self.description_text.delete("1.0", "end")
            self.location_entry.delete(0, "end")
            self.date_picker.set_date(date.today())
            self.hashtags.clear()
            self.refresh_hashtags_view()
            self.clear_photos()
            
    # --- GESTION HASHTAGS ---
    
    def normalize_hashtag(self, text: str) -> str:
        t = text.strip()
        if not t: return ""
        if ' ' in t: return ""
        if not t.startswith('#'): t = '#' + t
        return t

    def is_valid_hashtag(self, raw: str) -> bool:
        s = raw.strip()
        if not s or ' ' in s: return False
        if s.startswith('#'):
            core = s[1:]
            if not core: return False
            return core.isalnum() and len(core) <= self.MAX_HASHTAG_LEN and s.count('#') == 1
        return s.isalnum() and len(s) <= self.MAX_HASHTAG_LEN

    def add_hashtag(self):
        if len(self.hashtags) >= 3:
            messagebox.showerror("Hashtags", "Vous pouvez ajouter au maximum 3 hashtags.")
            return
        raw = self.hashtag_input.get()
        s = raw.strip()
        core = s[1:] if s.startswith('#') else s
        if len(core) > self.MAX_HASHTAG_LEN:
            messagebox.showerror("Hashtags", f"Un hashtag est limité à {self.MAX_HASHTAG_LEN} caractères maximum.")
            return
        if not self.is_valid_hashtag(raw):
            messagebox.showerror("Hashtags", "Hashtag invalide. Seules les lettres et chiffres sont autorisés. Le caractère # est autorisé uniquement au début.")
            return
        candidate = self.normalize_hashtag(raw)
        if not candidate or len(candidate) < 2:
            messagebox.showerror("Hashtags", "Hashtag invalide. Seules les lettres et chiffres sont autorisés. Le caractère # est autorisé uniquement au début.")
            return
        if candidate in self.hashtags:
            messagebox.showinfo("Doublon", "Ce hashtag est déjà ajouté.")
            return
        self.hashtags.append(candidate)
        self.hashtag_input.delete(0, "end")
        self.refresh_hashtags_view()

    def remove_hashtag(self, idx: int):
        if 0 <= idx < len(self.hashtags):
            self.hashtags.pop(idx)
            self.refresh_hashtags_view()

    def refresh_hashtags_view(self):
        for w in self.hashtags_container.winfo_children():
            w.destroy()
        if len(self.hashtags) >= 3:
            self.add_hashtag_btn.configure(state="disabled")
        else:
            self.add_hashtag_btn.configure(state="normal")
        if not self.hashtags:
            return
        grid = ctk.CTkFrame(self.hashtags_container, fg_color="transparent")
        grid.pack(anchor="w")
        for i, tag in enumerate(self.hashtags):
            chip = ctk.CTkFrame(grid, corner_radius=12)
            chip.grid(row=i//3, column=i%3, padx=4, pady=4, sticky="w")
            lbl = ctk.CTkLabel(chip, text=tag, padx=6, pady=2)
            lbl.pack(side="left")
            btn = ctk.CTkButton(chip, text="✕", width=18, height=18, command=lambda idx=i: self.remove_hashtag(idx), font=("Arial", 9))
            btn.pack(side="left", padx=(4,2), pady=2)