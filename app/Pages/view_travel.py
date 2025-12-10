import customtkinter as ctk
from datetime import datetime
from PIL import Image
import io
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.etapes import EtapesCRUD
from app.backend.crud.photo import PhotosCRUD

# Map Check
try:
    import tkintermapview
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

KNOWN_CITIES = {
    "Paris, France": (48.8566, 2.3522), "Marseille, France": (43.2965, 5.3698),
    "Lyon, France": (45.7640, 4.8357), "Londres, UK": (51.5074, -0.1278),
    "New York, USA": (40.7128, -74.0060), "Tokyo, Japon": (35.6762, 139.6503),
    "Rome, Italie": (41.9028, 12.4964), "Barcelone, Espagne": (41.3851, 2.1734),
    "Berlin, Allemagne": (52.5200, 13.4050), "Sydney, Australie": (-33.8688, 151.2093),
    "Dubai, UAE": (25.276987, 55.296249), "Rio de Janeiro, Brésil": (-22.9068, -43.1729),
    "Amsterdam, Pays-Bas": (52.3676, 4.9041), "Lisbonne, Portugal": (38.7223, -9.1393),
    "Bangkok, Thaïlande": (13.7563, 100.5018), "Los Angeles, USA": (34.0522, -118.2437),
    "San Francisco, USA": (37.7749, -122.4194), "Miami, USA": (25.7617, -80.1918),
    "Montréal, Canada": (45.5017, -73.5673), "Marrakech, Maroc": (31.6295, -7.9811),
    "Istanbul, Turquie": (41.0082, 28.9784)
}

class ViewTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        
        self.crud_voyage = VoyagesCRUD()
        self.crud_etape = EtapesCRUD()
        self.crud_photo = PhotosCRUD()
        
        self.voyage = self.crud_voyage.get_voyage(id_voyage)
        self.etapes = self.crud_etape.get_etapes_by_voyage(id_voyage)

        if not self.voyage:
            ctk.CTkLabel(self, text="Erreur: Voyage introuvable").pack()
            return

        self.setup_ui()

    def setup_ui(self):
        # 1. MAP (Haut)
        self.top_frame = ctk.CTkFrame(self, fg_color="#111", corner_radius=0)
        self.top_frame.pack(fill="both", expand=True, side="top")

        # Overlay
        overlay = ctk.CTkFrame(self.top_frame, fg_color="#2b2b2b", corner_radius=15, height=50, border_width=1, border_color="#444")
        overlay.place(relx=0.02, rely=0.03, relwidth=0.96)
        
        ctk.CTkButton(overlay, text="← Retour", command=lambda: self.master.show_page("ManageTravel"), 
                      width=90, fg_color="#444").pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(overlay, text=f"🌍 {self.voyage['nom_voyage']}", font=("Courgette", 22, "bold"), text_color="white").pack(side="left", padx=20)
        
        ctk.CTkButton(overlay, text="+ Ajouter une étape", command=lambda: self.master.show_page("CreateStage", id_item=self.id_voyage),
                      fg_color="#2CC985", font=("Arial", 12, "bold"), width=140).pack(side="right", padx=10)

        if MAP_AVAILABLE:
            self.map_widget = tkintermapview.TkinterMapView(self.top_frame, corner_radius=0)
            self.map_widget.pack(fill="both", expand=True, pady=(60, 0))
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=fr&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
            self.map_widget.set_position(48.8566, 2.3522)
            self.map_widget.set_zoom(4)
            self.after(200, self.add_markers_to_map)
        else:
            ctk.CTkLabel(self.top_frame, text="Module map manquant", text_color="gray").place(relx=0.5, rely=0.5, anchor="center")

        # 2. TIMELINE (Bas)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=350) # Plus haut pour les photos
        self.bottom_frame.pack(fill="x", side="bottom")

        ctk.CTkLabel(self.bottom_frame, text="📅 Carnet de Voyage", font=("Arial", 14, "bold"), text_color="#aaa").pack(anchor="w", padx=20, pady=(15,5))

        self.scroll = ctk.CTkScrollableFrame(self.bottom_frame, fg_color="transparent", height=260, orientation="horizontal")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=5)

        if not self.etapes:
            ctk.CTkLabel(self.scroll, text="Aucune étape... Cliquez sur '+ Ajouter' !", font=("Arial", 16)).pack(pady=80, padx=250)
        else:
            for idx, etape in enumerate(self.etapes):
                self.create_stage_card(etape, idx)

    def add_markers_to_map(self):
        if not MAP_AVAILABLE: return
        path_list = []
        for etape in self.etapes:
            lieu = etape['localisation']
            if not lieu: continue
            
            if lieu in KNOWN_CITIES:
                coords = KNOWN_CITIES[lieu]
                self.map_widget.set_marker(coords[0], coords[1], text=etape['nom_etape'])
                path_list.append(coords)
            else:
                try:
                    marker = self.map_widget.set_address(lieu, marker=True, text=etape['nom_etape'])
                    if marker: path_list.append(marker.position)
                except: pass
        
        if len(path_list) > 1: self.map_widget.set_path(path_list)
        elif len(path_list) == 1: self.map_widget.set_position(path_list[0][0], path_list[0][1], marker=True)

    def create_stage_card(self, etape, index):
        """Carte avec Photo à gauche."""
        # 1. Récupérer la photo depuis la BDD
        photo_data = self.crud_photo.get_photo_by_etape(etape['id_etape'])
        
        card_width = 300
        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=20, width=card_width, height=220)
        card.pack(side="left", padx=12, pady=5)
        card.pack_propagate(False)

        # Zone Image (Haut ou Gauche - ici Haut pour le style polaroid)
        img_frame = ctk.CTkFrame(card, fg_color="#000", height=120, corner_radius=15)
        img_frame.pack(fill="x", padx=0, pady=0)
        img_frame.pack_propagate(False)

        if photo_data and photo_data['photo']:
            try:
                # Conversion Binaire -> Image Tkinter
                pil_img = Image.open(io.BytesIO(photo_data['photo']))
                # Mode "Cover" (crop au centre)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(card_width, 120))
                lbl_img = ctk.CTkLabel(img_frame, text="", image=ctk_img)
                lbl_img.place(x=0, y=0)
            except Exception as e:
                ctk.CTkLabel(img_frame, text="Erreur Image", text_color="red").pack(expand=True)
        else:
            # Placeholder stylé
            ctk.CTkLabel(img_frame, text="📷 Pas de photo", text_color="gray").pack(expand=True)

        # Header texte
        txt_frame = ctk.CTkFrame(card, fg_color="transparent")
        txt_frame.pack(fill="both", expand=True, padx=10, pady=5)

        title = etape['nom_etape']
        if len(title) > 20: title = title[:18] + "..."
        ctk.CTkLabel(txt_frame, text=title, font=("Arial", 16, "bold"), text_color="white", anchor="w").pack(fill="x")

        if etape['localisation']:
             ctk.CTkLabel(txt_frame, text=f"📍 {etape['localisation']}", font=("Arial", 12), text_color="#2CC985", anchor="w").pack(fill="x")

        # Actions (Bas droite)
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="bottom", fill="x", padx=10, pady=8)

        ctk.CTkLabel(actions, text=f"#{index+1}", text_color="#00aaff", font=("Arial", 14, "bold")).pack(side="left")

        ctk.CTkButton(actions, text="🗑️", width=30, height=25, fg_color="#cf3030", hover_color="#a01010",
                      command=lambda: self.delete_stage(etape)).pack(side="right")
        ctk.CTkButton(actions, text="✏️", width=30, height=25, fg_color="#e6b800", hover_color="#b38f00",
                      command=lambda: self.master.show_page("EditStage", id_item=etape['id_etape'])).pack(side="right", padx=5)

    def delete_stage(self, etape):
        msg = CTkMessagebox(title="Supprimer ?", message="Voulez-vous supprimer cette étape et sa photo ?", icon="warning", option_1="Non", option_2="Oui")
        if msg.get() == "Oui":
            self.crud_etape.delete_etape(etape['id_etape'])
            self.master.show_travel_detail(self.id_voyage)