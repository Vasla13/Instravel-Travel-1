import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import datetime
import io
from typing import Dict, List, Any, Optional
import traceback # Ajout pour le débogage

# Import des CRUDs via le package app
from app.backend.database import get_db, close_db
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.commentaire import CommentairesCRUD
from app.backend.crud.photo import PhotosCRUD
from app.backend.crud.users import UsersCRUD
from app.backend.crud.hashtags import HashtagsCRUD 
# Import de EtapeHashtagCRUD si nécessaire pour les hashtags
from app.backend.crud.etape_hashtag import EtapeHashtagCRUD 


class StageView(ctk.CTkFrame):
    """Vue détaillée d'une étape (Stage)."""
    
    def __init__(self, parent, etape_id: int = 7, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.master = parent # Référence à l'Application
        
        # Initialisation des CRUDs (les connexions sont gérées par get_db/close_db)
        self.db = get_db()
        self.etapes_crud = EtapesCRUD(self.db)
        self.voyages_crud = VoyagesCRUD(self.db)
        self.commentaire_crud = CommentairesCRUD(self.db)
        self.photo_crud = PhotosCRUD(self.db)
        self.users_crud = UsersCRUD(self.db)
        self.hashtags_crud = HashtagsCRUD(self.db) # Ajout
        self.etape_hashtag_crud = EtapeHashtagCRUD(self.db) # Ajout
        
        self.etape_id = etape_id
        self.current_photo_index = 0
        self.current_photo = None # Référence à l'objet CTkImage affiché
        self.photos = []
        
        # Charger les données de l'étape
        self.etape_data = self.load_etape_data()
        
        if not self.etape_data:
            self.show_error(f"Erreur lors du chargement des données de l'étape #{self.etape_id}.")
            return
            
        self.setup_ui()
    
    def load_etape_data(self) -> Optional[dict]:
        """Charge toutes les infos nécessaires depuis la base (Étape, Voyage, Photos, Commentaires)."""
        try:
            # 1. Récupérer l'étape
            etape_result = self.etapes_crud.get_etape(self.etape_id)
            if not etape_result:
                return None

            etape = etape_result 
            # NOTE: Assurez-vous que etape_result est un dictionnaire si fetchone() est utilisé, ou ajustez l'indexation

            # 2. Récupérer le voyage associé (pour le bouton retour)
            voyage = self.voyages_crud.get_voyage(etape['id_voyage'])
            
            # 3. Récupérer l'utilisateur créateur du voyage
            user = self.users_crud.get_user(voyage['id_user']) if voyage and 'id_user' in voyage else None

            # 4. Récupérer les photos (BLOBs)
            photos_result = self.photo_crud.get_photos_by_etape(self.etape_id)
            photos = [p['photo'] for p in photos_result] if photos_result else []

            # 5. Récupérer les commentaires (NOTE: Assurez-vous que le CRUD Commentaires fait la jointure avec users)
            comments_result = self.commentaire_crud.get_commentaires_for_etape(self.etape_id)
            comments = []
            if comments_result:
                comments = [
                    {
                        "user": c.get('username', 'Anonyme'),
                        "date": c.get('date_comm').strftime("%d/%m/%Y %H:%M") if c.get('date_comm') else "",
                        "text": c.get('commentaire', '')
                    }
                    for c in comments_result
                ]
                
            # 6. Récupérer les hashtags
            hashtags_result = self.etape_hashtag_crud.get_hashtags_for_etape(self.etape_id)
            hashtags = [h.get('nom_hashtag', '') for h in hashtags_result] if hashtags_result else []

            return {
                "id_voyage_parent": etape.get("id_voyage"), # ID crucial pour le bouton retour
                "title": etape.get("nom_etape", "Sans titre"),
                "description": etape.get("description", "Aucune description"),
                "user": user.get("username", "Utilisateur inconnu") if user else "Utilisateur inconnu",
                "date": etape.get("date_etape").strftime("%d/%m/%Y") if etape.get("date_etape") else "Date inconnue",
                "photos": photos,
                "hashtags": hashtags,
                "comments": comments
            }

        except Exception as e:
            print(f"Erreur détaillée dans load_etape_data: {str(e)}")
            traceback.print_exc()
            return None

    
    def setup_ui(self):
        # ==== LAYOUT PRINCIPAL EN 2 COLONNES ====
        self.grid_columnconfigure(0, weight=2) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(1, weight=1) # Pour que le contenu s'étende verticalement

        # --- Header (Bouton Retour) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(15, 5))
        
        # Bouton Retour (Utilise l'ID voyage récupéré)
        ctk.CTkButton(
            header_frame, 
            text="← Retour au Voyage", 
            command=lambda: self.master.show_travel_detail(self.etape_data.get('id_voyage_parent')),
            width=150, height=35, fg_color="#3a3a3a", hover_color="#505050",
        ).pack(side="left")
        
        # ====== COLONNE GAUCHE : INFOS + IMAGES (row=1) ======
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_frame.grid_rowconfigure(0, weight=1) # Permet au contenu de gauche de s'étendre
        left_content_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        left_content_scroll.pack(fill="both", expand=True)

        # Titre
        self.title_label = ctk.CTkLabel(left_content_scroll, text=self.etape_data["title"], font=("Arial", 20, "bold"))
        self.title_label.pack(pady=(10, 5), anchor="w", padx=10)

        # Description
        self.desc_label = ctk.CTkLabel(left_content_scroll, text=self.etape_data["description"], 
                                       wraplength=450, justify="left")
        self.desc_label.pack(pady=(0, 10), anchor="w", padx=10)

        # Frame pour les infos utilisateur et date
        user_info_frame = ctk.CTkFrame(left_content_scroll, fg_color="transparent")
        user_info_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Nom de l'utilisateur
        self.user_label = ctk.CTkLabel(
            user_info_frame, 
            text=self.etape_data.get("user", "Utilisateur inconnu"),
            font=("Arial", 10, "bold")
        )
        self.user_label.pack(anchor="w")
        
        # Date de publication
        self.date_label = ctk.CTkLabel(
            user_info_frame,
            text=self.etape_data.get("date", "Date inconnue"),
            font=("Arial", 9, "italic"),
            text_color=("gray50", "gray70")
        )
        self.date_label.pack(anchor="w")

        # Image principale
        self.image_label = ctk.CTkLabel(left_content_scroll, text="Aucune image disponible", width=400, height=250, fg_color="#3a3a3a")
        self.image_label.pack(pady=5, padx=10)

        if self.etape_data.get("photos"):
            self.show_photo(0)

            btn_frame = ctk.CTkFrame(left_content_scroll, fg_color="transparent")
            btn_frame.pack(pady=5, padx=10)

            prev_btn = ctk.CTkButton(btn_frame, text="⏮️", width=40, command=self.prev_photo)
            prev_btn.grid(row=0, column=0, padx=5)

            next_btn = ctk.CTkButton(btn_frame, text="⏭️", width=40, command=self.next_photo)
            next_btn.grid(row=0, column=1, padx=5)
        
        # Hashtags
        hashtags = " ".join(self.etape_data.get("hashtags", []))
        if hashtags:
            self.hashtags_label = ctk.CTkLabel(left_content_scroll, text=hashtags, text_color="#00aaff", wraplength=450, justify="left")
            self.hashtags_label.pack(pady=(5, 10), anchor="w", padx=10)

        # ====== COLONNE DROITE : COMMENTAIRES (row=1) ======
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_rowconfigure(1, weight=1) 

        # Titre des commentaires
        ctk.CTkLabel(right_frame, text="Commentaires :", font=("Arial", 14, "bold"))\
            .pack(anchor="w", padx=10, pady=(10, 5))

        # Zone scrollable pour les commentaires
        self.comment_scroll = ctk.CTkScrollableFrame(right_frame, width=250, height=350)
        self.comment_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Afficher les commentaires existants
        for comment in self.etape_data.get("comments", []):
            self._add_comment_to_ui(comment)

        # Zone pour écrire un commentaire
        self.comment_entry = ctk.CTkEntry(right_frame, placeholder_text="Ajouter un commentaire...")
        self.comment_entry.pack(fill="x", padx=10, pady=(5, 5))
        self.comment_entry.bind("<Return>", lambda e: self.add_comment())

        self.add_comment_btn = ctk.CTkButton(right_frame, text="Poster", command=self.add_comment, fg_color="#00aaff", hover_color="#0088cc")
        self.add_comment_btn.pack(pady=(0, 10))
    
    def show_photo(self, index: int):
        """Affiche la photo à l'index donné."""
        if not self.etape_data.get("photos") or index < 0 or index >= len(self.etape_data["photos"]):
            return
            
        try:
            photo_data = self.etape_data["photos"][index]
            
            # On suppose que photo_data est un BLOB binaire
            img = Image.open(io.BytesIO(photo_data))
                
            # Redimensionner l'image pour l'affichage
            max_size = (400, 250)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir en format compatible avec CTk
            self.current_photo = ctk.CTkImage(
                light_image=img,
                size=img.size
            )
            
            self.image_label.configure(image=self.current_photo, text="")
            self.image_label.image = self.current_photo # Garder la référence!
            self.current_photo_index = index
            
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
            self.image_label.configure(text=f"Erreur image: {str(e)}")
    
    def next_photo(self):
        """Affiche la photo suivante."""
        if not self.etape_data.get("photos"):
            return
        self.current_photo_index = (self.current_photo_index + 1) % len(self.etape_data["photos"])
        self.show_photo(self.current_photo_index)
    
    def prev_photo(self):
        """Affiche la photo précédente."""
        if not self.etape_data.get("photos"):
            return
        self.current_photo_index = (self.current_photo_index - 1) % len(self.etape_data["photos"])
        self.show_photo(self.current_photo_index)
    
    def add_comment(self):
        """Ajoute un nouveau commentaire."""
        comment_text = self.comment_entry.get().strip()
        if not comment_text:
            return
        
        # NOTE: Vous devez gérer l'ID utilisateur connecté (self.master.current_user_id)
        # et l'ID étape (self.etape_id) dans le CRUD.
        
        try:
            # Implémentation réelle de la BDD (supposée pour le moment)
            # self.commentaire_crud.create_commentaire(
            #     commentaire=comment_text,
            #     id_user=self.master.current_user_id,
            #     id_etape=self.etape_id
            # )
            
            new_comment = {
                "user": "Utilisateur Actuel", # Remplacez par le nom d'utilisateur réel
                "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                "text": comment_text
            }
            
            self._add_comment_to_ui(new_comment)
            self.comment_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Erreur Commentaire", f"Erreur lors de l'ajout du commentaire: {e}")
    
    def _add_comment_to_ui(self, comment_data: Dict[str, Any]):
        """Ajoute un commentaire à l'interface utilisateur."""
        # ... (Logique d'affichage UI inchangée) ...
        comment_frame = ctk.CTkFrame(self.comment_scroll, fg_color=("gray90", "gray16"), corner_radius=5)
        comment_frame.pack(fill="x", pady=3, padx=2)
        
        header_frame = ctk.CTkFrame(comment_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        
        user_label = ctk.CTkLabel(
            header_frame, 
            text=comment_data.get("user", "Anonyme"),
            font=("Arial", 10, "bold")
        )
        user_label.pack(side="left", padx=(0, 5))
        
        date_label = ctk.CTkLabel(
            header_frame,
            text=comment_data.get("date", ""),
            font=("Arial", 8, "italic"),
            text_color=("gray50", "gray70")
        )
        date_label.pack(side="left")
        
        comment_label = ctk.CTkLabel(
            comment_frame,
            text=comment_data.get("text", ""),
            wraplength=230,
            justify="left",
            anchor="w"
        )
        comment_label.pack(fill="x", padx=10, pady=(0, 8))
    
    def show_error(self, message: str):
        """Affiche un message d'erreur."""
        error_label = ctk.CTkLabel(
            self, 
            text=message,
            text_color="red",
            font=("Arial", 12, "bold")
        )
        error_label.pack(pady=20)
    
    def __del__(self):
        """Ferme la connexion à la base de données lors de la destruction de l'objet."""
        if hasattr(self, 'db') and self.db:
            close_db()