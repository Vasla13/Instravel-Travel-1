import customtkinter as ctk
from datetime import datetime
from CTkMessagebox import CTkMessagebox
from app.backend.crud.voyages import VoyagesCRUD
from app.backend.crud.etapes import EtapesCRUD

# Vérification du module carte
try:
    import tkintermapview
    MAP_AVAILABLE = True
except ImportError:
    MAP_AVAILABLE = False

class ViewTravelView(ctk.CTkFrame):
    def __init__(self, parent, id_voyage: int):
        super().__init__(parent)
        self.master = parent
        self.id_voyage = id_voyage
        
        self.crud_voyage = VoyagesCRUD()
        self.crud_etape = EtapesCRUD()
        
        # Données
        self.voyage = self.crud_voyage.get_voyage(id_voyage)
        self.etapes = self.crud_etape.get_etapes_by_voyage(id_voyage)

        if not self.voyage:
            ctk.CTkLabel(self, text="Erreur: Voyage introuvable").pack()
            return

        self.setup_ui()

    def setup_ui(self):
        # 1. Zone CARTE (Haut - 60% hauteur)
        self.top_frame = ctk.CTkFrame(self, fg_color="#111", corner_radius=0)
        self.top_frame.pack(fill="both", expand=True, side="top")

        # Header Flottant (par-dessus la carte)
        overlay = ctk.CTkFrame(self.top_frame, fg_color="#2b2b2b", corner_radius=15, height=50, border_width=1, border_color="#444")
        overlay.place(relx=0.02, rely=0.03, relwidth=0.96)
        
        ctk.CTkButton(overlay, text="← Retour", command=lambda: self.master.show_page("ManageTravel"), 
                      width=80, fg_color="#444", hover_color="#333").pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(overlay, text=f"🌍 {self.voyage['nom_voyage']}", font=("Courgette", 20, "bold"), text_color="white").pack(side="left", padx=20)
        
        ctk.CTkButton(overlay, text="+ Ajouter une étape", command=lambda: self.master.show_page("CreateStage", id_item=self.id_voyage),
                      fg_color="#2CC985", hover_color="#1e8558", font=("Arial", 12, "bold")).pack(side="right", padx=10)

        # Affichage Carte
        if MAP_AVAILABLE:
            self.map_widget = tkintermapview.TkinterMapView(self.top_frame, corner_radius=0)
            self.map_widget.pack(fill="both", expand=True, pady=(60, 0)) # Padding pour laisser le header visible
            
            # --- FIX CRITIQUE : Utiliser Google Maps pour éviter l'erreur 403 ---
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=fr&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
            
            # Position défaut (Paris)
            self.map_widget.set_position(48.8566, 2.3522)
            self.map_widget.set_zoom(5)
            
            # Charger les points après 500ms pour fluidité
            self.after(500, self.add_markers_to_map)
        else:
            ctk.CTkLabel(self.top_frame, text="Module 'tkintermapview' non installé.", text_color="gray").place(relx=0.5, rely=0.5, anchor="center")

        # 2. Zone TIMELINE (Bas - Liste horizontale)
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", height=280)
        self.bottom_frame.pack(fill="x", side="bottom")

        ctk.CTkLabel(self.bottom_frame, text="📅  Chronologie de votre voyage", font=("Arial", 14, "bold"), text_color="#888").pack(anchor="w", padx=20, pady=(10,5))

        self.scroll = ctk.CTkScrollableFrame(self.bottom_frame, fg_color="transparent", height=200, orientation="horizontal")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=5)

        if not self.etapes:
            ctk.CTkLabel(self.scroll, text="Ce voyage est vide...\nAjoutez votre première étape !", font=("Arial", 16)).pack(pady=60, padx=200)
        else:
            for idx, etape in enumerate(self.etapes):
                self.create_stage_card(etape, idx)

    def add_markers_to_map(self):
        """Ajoute les points sur la carte sans faire planter l'appli."""
        if not MAP_AVAILABLE: return
        path_list = []
        
        for etape in self.etapes:
            if etape['localisation']:
                try:
                    # set_address peut échouer si pas d'internet ou ville inconnue
                    marker = self.map_widget.set_address(etape['localisation'], marker=True, text=etape['nom_etape'])
                    if marker:
                        path_list.append(marker.position)
                except Exception:
                    print(f"Lieu non trouvé : {etape['localisation']}")

        # Relier les points si possible
        if len(path_list) > 1:
            self.map_widget.set_path(path_list)
        elif len(path_list) == 1:
            self.map_widget.set_position(path_list[0][0], path_list[0][1])
            self.map_widget.set_zoom(10)

    def create_stage_card(self, etape, index):
        """Petite carte pour chaque étape."""
        card = ctk.CTkFrame(self.scroll, fg_color="#2b2b2b", corner_radius=15, width=240, height=160)
        card.pack(side="left", padx=10, pady=5)
        card.pack_propagate(False) # Garder la taille fixe

        # Header Carte
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(top, text=f"#{index + 1}", font=("Arial", 20, "bold"), text_color="#00aaff").pack(side="left")
        
        # Date à droite
        d_str = ""
        try: d_str = etape['date_etape'].strftime("%d/%m")
        except: pass
        ctk.CTkLabel(top, text=d_str, font=("Arial", 12), text_color="gray").pack(side="right")

        # Titre
        title = etape['nom_etape']
        if len(title) > 22: title = title[:20] + "..."
        ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color="white", anchor="w").pack(fill="x", padx=15)

        # Lieu
        if etape['localisation']:
             ctk.CTkLabel(card, text=f"📍 {etape['localisation']}", font=("Arial", 11), text_color="#2CC985", anchor="w").pack(fill="x", padx=15)

        # Actions (Bas)
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(side="bottom", fill="x", padx=10, pady=10)

        # Edit
        ctk.CTkButton(actions, text="Modifier", width=80, height=28, fg_color="#444", hover_color="#555", font=("Arial", 11),
                      command=lambda: self.master.show_page("EditStage", id_item=etape['id_etape'])).pack(side="left")
        
        # Delete
        ctk.CTkButton(actions, text="🗑️", width=30, height=28, fg_color="#ff4d4d", hover_color="#cc0000",
                      command=lambda: self.delete_stage(etape)).pack(side="right")

    def delete_stage(self, etape):
        msg = CTkMessagebox(title="Supprimer ?", message="Voulez-vous supprimer cette étape ?", icon="warning", option_1="Non", option_2="Oui")
        if msg.get() == "Oui":
            self.crud_etape.delete_etape(etape['id_etape'])
            self.master.show_travel_detail(self.id_voyage)