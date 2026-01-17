import tkinter as tk
from datetime import datetime

from ui.dashboard import DashboardFrame
from ui.ventes import VentesFrame
from ui.produits import ProduitsFrame
from ui.categories import CategorieFrame
from ui.fournisseurs import FournisseurFrame
from ui.commandes import CommandeAchatFrame
from ui.stock import StockFrame
from ui.reçus import ReçusFrame
from ui.rapports import RapportsFrame
from ui.employe import EmployeFrame


class BaseFrame(tk.Frame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, bg='white')
        self.pack(fill=tk.BOTH, expand=True)

        self.user = user
        self.on_logout = on_logout

        self.create_header()
        self.create_subtitle()
        self.create_sidebar()
        self.create_content()

    # ===================== HEADER =====================
    def create_header(self):
        header = tk.Frame(self, bg='#010c48', height=70)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        self.title_image = tk.PhotoImage(file="assets/shop.png")

        tk.Label(
            header,
            image=self.title_image,
            compound=tk.RIGHT,
            text="Système de gestion de magasin",
            font=('times new roman', 25, 'bold'),
            bg='#010c48',
            fg='white',
            anchor='w',
            padx=17
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        user_info = tk.Frame(header, bg='#010c48')
        user_info.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            user_info,
            text=self.user["nom"],
            font=('times new roman', 14, 'bold'),
            bg='#010c48',
            fg='white'
        ).pack(anchor='w')

        tk.Label(
            user_info,
            text=self.user["role"],
            font=('times new roman', 11),
            bg='#010c48',
            fg='#d1d5db'
        ).pack(anchor='w')

        tk.Button(
            header,
            text="Déconnexion",
            command=self.logout,
            bd=0,
            bg='white',
            fg='#010c48',
            font=('times new roman', 15, 'bold'),
            cursor='hand2'
        ).pack(side=tk.RIGHT, padx=20)

    # ===================== SUBTITLE =====================
    def create_subtitle(self):
        self.subtitle = tk.Frame(self, bg='#4d636d', height=35)
        self.subtitle.pack(side=tk.TOP, fill=tk.X)
        self.subtitle.pack_propagate(False)

        self.subtitle_label = tk.Label(
            self.subtitle,
            font=('times new roman', 15),
            bg='#4d636d',
            fg='white'
        )
        self.subtitle_label.pack(side=tk.LEFT, padx=10)

        self.update_time()

    def update_time(self):
        now = datetime.now().strftime("Date: %d-%m-%Y\t\tTime: %H:%M:%S")
        self.subtitle_label.config(
            text=f"\t\t\t\tBienvenue {self.user['nom']}\t\t{now}"
        )
        self.after(1000, self.update_time)

    # ===================== SIDEBAR =====================
    def create_sidebar(self):
        self.sidebar = tk.Frame(self, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="Menu",
            font=('times new roman', 20),
            bg='#009688',
            fg='white'
        ).pack(fill=tk.X)

        MENU_CONFIG = {
            "ADMIN": [
                ("🏠 Dashboard", DashboardFrame),
                ("👥 Employés", EmployeFrame),
                ("🏭 Fournisseurs", FournisseurFrame),
                ("📁 Catégories", CategorieFrame),
                ("📦 Produits", ProduitsFrame),
                ("💰 Ventes", VentesFrame),
                ("📋 Commandes", CommandeAchatFrame),
                ("📊 Stock", StockFrame),
                ("🧾 Reçus", ReçusFrame),
                ("📈 Rapports", RapportsFrame),
            ],

            "CAISSIER": [
                ("🏠 Dashboard", DashboardFrame),
                ("💰 Ventes", VentesFrame),
                ("🧾 Reçus", ReçusFrame),
            ],

            "GESTIONNAIRE_STOCK": [
                ("🏠 Dashboard", DashboardFrame),
                ("📁 Catégories", CategorieFrame),
                ("📦 Produits", ProduitsFrame),
                ("📊 Stock", StockFrame),
            ],

            "RESPONSABLE_ACHAT": [
                ("🏠 Dashboard", DashboardFrame),
                ("🏭 Fournisseurs", FournisseurFrame),
                ("📋 Commandes", CommandeAchatFrame),
            ]
        }

        menus = MENU_CONFIG.get(self.user["role"], [])

        for label, frame_class in menus:
            tk.Button(
                self.sidebar,
                text=label,
                font=('times new roman', 19, 'bold'),
                anchor='w',
                cursor='hand2',
                command=lambda f=frame_class: self.show_page(f)
            ).pack(fill=tk.X)

    # ===================== CONTENT =====================
    def create_content(self):
        self.content = tk.Frame(self, bg='#f5f6f8')
        self.content.pack(fill=tk.BOTH, expand=True)

        self.show_page(DashboardFrame)

    # ===================== NAVIGATION =====================

    def show_page(self, frame_class):
        # Supprimer l'ancienne page
        for widget in self.content.winfo_children():
            widget.destroy()

        # Réinitialiser la disposition complète
        self.sidebar.pack_forget()
        self.content.pack_forget()

        # Cacher le menu
        FULLSCREEN_PAGES = {VentesFrame,StockFrame,CommandeAchatFrame,RapportsFrame}

        if frame_class in FULLSCREEN_PAGES:

            # Seulement le contenu (full screen)
            self.content.pack(fill=tk.BOTH, expand=True)
        else:
            # Sidebar + contenu
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
            self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        page = frame_class(
            self.content,
            user = self.user,
            go_dashboard=lambda: self.show_page(DashboardFrame)
        )
        page.pack(fill=tk.BOTH, expand=True)


    # ===================== LOGOUT =====================
    def logout(self):
        self.on_logout()
