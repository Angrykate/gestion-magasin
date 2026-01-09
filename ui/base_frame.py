import tkinter as tk
from datetime import datetime


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

        # Titre + logo (gauche, prend l'espace)
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

        # Bloc infos utilisateur (à gauche du bouton)
        user_info = tk.Frame(header, bg='#010c48')
        user_info.pack(side=tk.LEFT, padx=20, pady=10)

        tk.Label(
            user_info,
            text=self.user["nom"],
            font=('times new roman', 14, 'bold'),
            bg='#010c48',
            fg='white',
            anchor='w'
        ).pack(anchor='w')

        tk.Label(
            user_info,
            text=self.user["role"],
            font=('times new roman', 11),
            bg='#010c48',
            fg='#d1d5db',
            anchor='w'
        ).pack(anchor='w')

        # Bouton déconnexion (TOUT À DROITE)
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
        sidebar = tk.Frame(self, width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Menu",
            font=('times new roman', 20),
            bg='#009688',
        ).pack(fill=tk.X)

        menus = [
            "🏠 Dashboard", "👥 Employés", "🏭 Fournisseurs", "📁 Catégories",
            "📦 Produits", "💰 Ventes", "📋 Commandes",
            "📊 Stock", "🧾 Reçus", "📈 Rapports"
        ]

        for menu in menus:
            tk.Button(
                sidebar,
                text=menu,
                font=('times new roman', 19, 'bold'),
                anchor='w',
                cursor='hand2'
            ).pack(fill=tk.X)

    # ===================== CONTENT =====================
    def create_content(self):
        self.content = tk.Frame(self, bg='#f5f6f8')
        self.content.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self.content,
            text="Bienvenue sur le Dashboard",
            font=('times new roman', 18, 'bold')
        ).pack(pady=50)
        print("Création du contenu BaseFrame")

    # ===================== LOGOUT =====================
    def logout(self):
        self.on_logout()
