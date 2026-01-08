import tkinter as tk
from datetime import datetime

class BaseFrame(tk.Frame):
    def __init__(self, parent, user_name="Admin", user_role="Administrateur"):
        super().__init__(parent, bg='white')
        self.pack(fill=tk.BOTH, expand=True)

        self.user_name = user_name
        self.user_role = user_role

        self.create_header()
        self.create_subtitle()
        self.create_sidebar()
        self.create_content_area()

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
        ).pack(side=tk.LEFT, padx=17)

        right_container = tk.Frame(header, bg='#010c48')
        right_container.pack(side=tk.RIGHT, padx=20, pady=10)

        tk.Button(
            right_container,
            text="Déconnexion",
            bg='white',
            fg='#010c48',
            font=('times new roman', 15, 'bold'),
            cursor='hand2'
        ).pack(side=tk.RIGHT)

        user_frame = tk.Frame(right_container, bg='#010c48')
        user_frame.pack(side=tk.RIGHT,padx=(0, 90))

        tk.Label(
            user_frame,
            text=self.user_name,
            font=('times new roman', 14, 'bold'),
            bg='#010c48',
            fg='white',
            anchor='e'
        ).pack(anchor='e')

        tk.Label(
            user_frame,
            text=self.user_role,
            font=('times new roman', 11),
            bg='#010c48',
            fg='#d1d5db',
            anchor='e'
        ).pack(anchor='e')

    def update_time(self):
        now = datetime.now().strftime("Date: %d-%m-%Y\t\t Time: %H:%M:%S")
        self.subtitle_label.config(
            text=f"\t\t\t\tBienvenue {self.user_name}\t\t {now}"
        )
        # Rappel automatique toutes les secondes
        self.after(1000, self.update_time)

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

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg='#009688', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.X)

        tk.Label(
            sidebar,
            text="Menu",
            font=('times new roman', 20),
            bg='#009688',
        ).pack(fill=tk.X)

        menus = [
            "Dashboard", "👥 Employés", "🏭 Fournisseurs", "📁 Catégories",
            "📦 Produits", "💰 Ventes", "📋 Commandes", "📊 Stock", "🧾 Reçus", "📈 Rapports"
        ]

        for menu in menus:
            tk.Button(
                sidebar,
                text=menu,
                font=('times new roman', 19, 'bold'),
                anchor='w',
            ).pack(fill=tk.X)

    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg='#e9ecef')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
