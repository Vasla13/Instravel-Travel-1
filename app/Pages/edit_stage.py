import customtkinter as ctk
from PIL import Image
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
from typing import List, Optional
import io
import os
import re

from app.backend.database import get_db
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.etape_hashtag import EtapeHashtagCRUD
from app.backend.crud.photo import PhotosCRUD
from app.backend.crud.hashtags import HashtagsCRUD


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


class EditStageView(ctk.CTkFrame):
    """Page d'édition d'une étape existante."""

    def __init__(self, parent, etape_id: int = 7, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.master = parent
        self.etape_id = etape_id
        
        # NOUVEAU: ID du voyage parent, chargé depuis la BDD
        self.id_voyage_parent: Optional[int] = None 
        
        self.selected_new_photos: List[str] = []
        self.current_photo_thumbs: List[ctk.CTkImage] = []
        self.hashtags: List[str] = []
        self.MAX_HASHTAG_LEN = 10

        # Layout principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, width=760, height=460)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_container.grid_propagate(False)

        title_label = ctk.CTkLabel(self.main_container, text=f"Modifier l'étape #{self.etape_id}", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 5))

        content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content.pack(fill="x")

        self.left = ctk.CTkFrame(content)
        self.left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        self.right = ctk.CTkFrame(content)
        self.right.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        ctk.CTkLabel(self.left, text="Informations principales", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(5, 10))

        # Champs
        ctk.CTkLabel(self.left, text="Titre de l'étape *").pack(anchor="w", padx=10)
        self.title_entry = ctk.CTkEntry(self.left, width=320)
        self.title_entry.pack(anchor="w", padx=10, pady=(2, 5))

        ctk.CTkLabel(self.left, text="Description *").pack(anchor="w", padx=10)
        self.description_text = ctk.CTkTextbox(self.left, width=320, height=30)
        self.description_text.pack(anchor="w", padx=10, pady=(2, 5))
        # Rendre la zone de description non-scrollable (désactive la molette)
        self.description_text.bind("<MouseWheel>", lambda e: "break")
        self.description_text.bind("<Button-4>", lambda e: "break")
        self.description_text.bind("<Button-5>", lambda e: "break")

        ctk.CTkLabel(self.left, text="Localisation *").pack(anchor="w", padx=10)
        self.location_entry = ctk.CTkEntry(self.left, width=320)
        self.location_entry.pack(anchor="w", padx=10, pady=(2, 5))

        ctk.CTkLabel(self.left, text="Date *").pack(anchor="w", padx=10)
        date_container = ctk.CTkFrame(self.left, width=150, height=28)
        date_container.pack_propagate(False)
        date_container.pack(anchor="w", padx=10, pady=(2, 5))
        self.date_picker = DateEntry(master=date_container, state="readonly", date_pattern="dd/MM/yyyy", locale="fr_FR")
        self.date_picker.config(width=12)
        self.date_picker.pack(fill="both", expand=True)

        hashtag_header = ctk.CTkFrame(self.left, fg_color="transparent")
        hashtag_header.pack(fill="x", padx=10, pady=(5, 5))
        ctk.CTkLabel(hashtag_header, text="Hashtags").pack(side="left")
        # Champ + bouton '+' sur la même ligne
        hashtag_row = ctk.CTkFrame(self.left)
        hashtag_row.pack(anchor="w", padx=10, pady=(0, 6))
        self.hashtag_input = ctk.CTkEntry(hashtag_row, width=280, placeholder_text="Maximum 3 # et 10 caractères")
        self.hashtag_input.pack(side="left")
        self.add_hashtag_btn = ctk.CTkButton(hashtag_row, text="+", width=28, command=self.add_hashtag)
        self.add_hashtag_btn.pack(side="left", padx=(8, 0))
        # Ajout via Entrée
        self.hashtag_input.bind("<Return>", lambda e: self.add_hashtag())
        self.hashtags_container = ctk.CTkFrame(self.left, fg_color="transparent")
        self.hashtags_container.pack(anchor="w", padx=10, pady=(0, 10))
        self.refresh_hashtags_view()

        # Photos à droite
        ctk.CTkLabel(self.right, text="Photos", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=(5, 10))
        photo_buttons = ctk.CTkFrame(self.right)
        photo_buttons.pack(anchor="w", padx=10, pady=(0, 5))

        self.add_photo_btn = ctk.CTkButton(photo_buttons, text="📷 Ajouter", command=self.choose_new_photos, width=110)
        self.add_photo_btn.pack(side="left", padx=(0, 5))

        self.clear_new_btn = ctk.CTkButton(photo_buttons, text="🗑️ Effacer", command=self.clear_new_selection, width=120)
        self.clear_new_btn.pack(side="left")

        self.photos_preview_frame = ctk.CTkFrame(self.right, height=240, width=350, fg_color="transparent")
        self.photos_preview_frame.pack(fill="y", expand=True, padx=10, pady=(0, 5))
        self.photos_preview_frame.pack_propagate(False)
        # Label d'info / compteur
        self.photos_info_label = ctk.CTkLabel(self.photos_preview_frame, text="Aucune nouvelle photo sélectionnée (max 6)")
        self.photos_info_label.pack(pady=10)

        # Boutons action
        actions = ctk.CTkFrame(self.right)
        actions.pack(pady=(5, 10), padx=10)
        self.save_btn = ctk.CTkButton(actions, text="💾 Enregistrer", command=self.save_changes, width=120, height=35)
        self.save_btn.pack(side="left", padx=(0, 10))
        
        # Bouton Annuler/Retour
        self.cancel_btn = ctk.CTkButton(actions, text="❌ Annuler", command=self.cancel_edit, width=100, height=35)
        self.cancel_btn.pack(side="left")

        # Charger données existantes
        self.load_existing_data()

    def load_existing_data(self):
        db = get_db()
        etapes = EtapesCRUD(db)
        photos = PhotosCRUD(db)
        hashtags = EtapeHashtagCRUD(db)

        etape = etapes.get_etape(self.etape_id)
        if not etape:
            messagebox.showerror("Erreur", f"Étape #{self.etape_id} introuvable")
            return

        # NOUVEAU: Stocker l'ID du voyage parent
        self.id_voyage_parent = etape.get("id_voyage") 

        # Prefill champs
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, etape.get("nom_etape", ""))

        self.description_text.delete("1.0", "end")
        self.description_text.insert("1.0", etape.get("description", ""))

        self.location_entry.delete(0, "end")
        self.location_entry.insert(0, etape.get("localisation", ""))

        d = etape.get("date_etape")
        if isinstance(d, (date, datetime)):
            self.date_picker.set_date(d)

        # Hashtags
        tags = hashtags.get_hashtags_for_etape(self.etape_id)
        self.hashtags = []
        if tags:
            for h in tags:
                t = h.get("nom_hashtag", "").strip()
                if not t:
                    continue
                if not t.startswith('#'):
                    t = '#' + t
                if t not in self.hashtags:
                    self.hashtags.append(t)
                if len(self.hashtags) >= 3:
                    break
        self.refresh_hashtags_view()

        # Photos existantes (affiche des vignettes à partir des blobs)
        self.show_existing_photos(photos)
        # Aperçu des nouvelles photos (vide au départ)
        self.update_new_photos_preview()

    def show_existing_photos(self, photos_crud: PhotosCRUD):
        for widget in self.photos_preview_frame.winfo_children():
            widget.destroy()
        self.current_photo_thumbs.clear()

        db_photos = photos_crud.get_photos_by_etape(self.etape_id)
        if not db_photos:
            ctk.CTkLabel(self.photos_preview_frame, text="Aucune photo actuelle").pack(pady=10)
            self.photos_info_label = ctk.CTkLabel(self.photos_preview_frame, text="Aucune nouvelle photo sélectionnée (max 6)")
            self.photos_info_label.pack(pady=10)
            return

        grid = ctk.CTkFrame(self.photos_preview_frame, fg_color="transparent")
        grid.pack(expand=True, padx=5, pady=5)
        for idx, p in enumerate(db_photos):
            try:
                blob = p.get("photo")
                img = Image.open(io.BytesIO(blob))
                img.thumbnail((90, 90))
                thumb = ctk.CTkImage(light_image=img, size=(90, 90))
                self.current_photo_thumbs.append(thumb)
                cell = ctk.CTkLabel(grid, image=thumb, text="")
                cell.grid(row=idx // 3, column=idx % 3, padx=4, pady=4)
            except Exception as e:
                ctk.CTkLabel(grid, text=f"Erreur image #{idx}").grid(row=idx // 3, column=idx % 3)
        self.photos_info_label = ctk.CTkLabel(self.photos_preview_frame, text="Aucune nouvelle photo sélectionnée (max 6)")
        self.photos_info_label.pack(pady=10)

    def choose_new_photos(self):
        file_types = [
            ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("JPEG", "*.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("Tous les fichiers", "*.*")
        ]
        remaining = 6 - len(self.selected_new_photos)
        if remaining <= 0:
            messagebox.showwarning("Limite atteinte", "Vous ne pouvez sélectionner que 6 photos maximum.")
            return
        files = filedialog.askopenfilenames(title=f"Sélectionner des photos (max {remaining} restantes)", filetypes=file_types)
        if files:
            to_add = list(files)[:remaining]
            if len(files) > remaining:
                messagebox.showinfo("Limite de photos", f"Seules les {remaining} premières photos ont été ajoutées (limite de 6 photos).")
            self.selected_new_photos.extend(to_add)
            self.update_new_photos_preview()

    def clear_new_selection(self):
        self.selected_new_photos.clear()
        self.update_new_photos_preview()

    def update_new_photos_preview(self):
        for widget in self.photos_preview_frame.winfo_children():
            widget.destroy()
        if not self.selected_new_photos:
            self.photos_info_label = ctk.CTkLabel(self.photos_preview_frame, text="Aucune nouvelle photo sélectionnée")
            self.photos_info_label.pack(pady=20)
            counter_label = ctk.CTkLabel(self.photos_preview_frame, text="0/6 photos", font=("Arial", 10))
            counter_label.pack()
            return

        thumbnails_container = ctk.CTkFrame(self.photos_preview_frame, fg_color="transparent")
        thumbnails_container.pack(fill="both", expand=True, padx=5, pady=5)

        grid = ctk.CTkFrame(thumbnails_container, fg_color="transparent")
        grid.pack(expand=True, padx=5, pady=5)
        for col in range(min(3, len(self.selected_new_photos))):
            grid.grid_columnconfigure(col, weight=1, minsize=105)

        for i, path in enumerate(self.selected_new_photos):
            try:
                img = Image.open(path)
                img.thumbnail((90, 90))
                cell = ctk.CTkFrame(grid, width=105, height=115)
                cell.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="nsew")
                cell.grid_propagate(False)

                photo_tk = ctk.CTkImage(light_image=img, size=(90, 90))
                img_label = ctk.CTkLabel(cell, image=photo_tk, text="")
                img_label.image = photo_tk
                img_label.pack(pady=(3,1))

                remove_btn = ctk.CTkButton(cell, text="✕", width=18, height=18, command=lambda idx=i: self.remove_new_photo(idx), font=("Arial", 9))
                remove_btn.pack(pady=(0,3))
            except Exception:
                ctk.CTkLabel(grid, text=f"Erreur img").grid(row=i//3, column=i%3)

        counter_label = ctk.CTkLabel(thumbnails_container, text=f"{len(self.selected_new_photos)}/6 photos", font=("Arial", 10))
        counter_label.pack(pady=(5,0))

    def remove_new_photo(self, idx: int):
        if 0 <= idx < len(self.selected_new_photos):
            self.selected_new_photos.pop(idx)
            self.update_new_photos_preview()

    def save_changes(self):
        """Enregistre les modifications sur l'étape. Redirige vers ViewTravelView en cas de succès."""
        db = get_db()
        etapes = EtapesCRUD(db)
        hashtags = EtapeHashtagCRUD(db)
        tags_crud = HashtagsCRUD(db)
        photos = PhotosCRUD(db)

        # Récup champs
        title = self.title_entry.get().strip()
        desc = self.description_text.get("1.0", "end-1c").strip()
        loc = self.location_entry.get().strip()
        selected_date = self.date_picker.get_date()
        date_str = selected_date.strftime("%d/%m/%Y") if selected_date else ""
        date_sql = format_date_for_mysql(date_str)

        if not title or not desc or not loc or not date_sql:
            messagebox.showerror("Champs requis", "Titre, description, localisation et date sont obligatoires.")
            return
        if len(self.hashtags) > 3:
            messagebox.showerror("Hashtags", "Maximum 3 hashtags autorisés.")
            return
        for tag in self.hashtags:
            if not tag.startswith('#') or len(tag) < 2 or not tag[1:].isalnum() or len(tag[1:]) > self.MAX_HASHTAG_LEN:
                messagebox.showerror("Hashtags", f"Hashtag invalide: {tag}. Seules les lettres et chiffres sont autorisés (max {self.MAX_HASHTAG_LEN}), et '#' uniquement au début.")
                return

        try:
            # Update étape
            etapes.update_etape(self.etape_id, nom_etape=title, description=desc, localisation=loc, date_etape=date_sql)

            # Update hashtags
            hashtags.delete_all_for_etape(self.etape_id)
            if self.hashtags:
                for tag in set(self.hashtags):
                    id_hashtag = tags_crud.get_or_create(tag)
                    hashtags.add_hashtag_to_etape(self.etape_id, id_hashtag)

            # Remplacement des photos si nouvelles sélectionnées
            if self.selected_new_photos:
                photos.delete_photos_for_etape(self.etape_id)
                for path in self.selected_new_photos:
                    with open(path, "rb") as f:
                        blob = f.read()
                    photos.create_photo(blob, self.etape_id)

            db.commit()
            messagebox.showinfo("Succès", "Étape mise à jour avec succès")
            
            # ⚠️ REDIRECTION VERS VIEW TRAVEL ⚠️
            if self.id_voyage_parent:
                self.master.show_travel_detail(self.id_voyage_parent) 
            else:
                self.master.show_page("ManageTravel") # Retour de secours

        except Exception as e:
            # CORRECTION ROLLBACK
            try:
                if hasattr(db.cursor, 'connection') and db.cursor.connection:
                    db.cursor.connection.rollback()
            except Exception:
                pass 
            messagebox.showerror("Erreur", f"Impossible de mettre à jour l'étape : {e}")

    def cancel_edit(self):
        """Annule les modifications et retourne à la vue du voyage parent."""
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir annuler les modifications ?"):
            # Si nous avons l'ID du voyage parent, retour direct à la vue détaillée
            if self.id_voyage_parent:
                self.master.show_travel_detail(self.id_voyage_parent)
            else:
                self.master.show_page("ManageTravel") # Retour de secours
                
    # ==================== GESTION HASHTAGS (Fonctions inchangées) ====================
    
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