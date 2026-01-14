import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


class StockFrame(tk.Frame):
    def __init__(self, parent,user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)

        self.go_dashboard = go_dashboard

        self.create_title()
        self.create_stats_frame()
        self.create_main_content()

        # Charger les données
        self.load_stats()
        self.load_stock_status()
        self.load_stock_history()

    # ===================== TITRE =====================
    def create_title(self):
        title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        title_bar.pack(fill=tk.X)

        if self.go_dashboard:
            tk.Button(
                title_bar,
                text="⬅ Dashboard",
                font=('times new roman', 11, 'bold'),
                bg='#ffffff',
                fg='#0f4d7d',
                cursor='hand2',
                command=self.go_dashboard
            ).pack(side=tk.LEFT, padx=10)

        tk.Label(
            title_bar,
            text='📦 Gestion du Stock',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== STATISTIQUES (HAUT) =====================
    def create_stats_frame(self):
        stats_frame = tk.Frame(self, bg='#f5f6f8')
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        # Carte 1 : Total articles
        total_card = self.create_stat_card(
            stats_frame,
            "Total articles en stock",
            "1,245",
            "#0d6efd",
            "📊"
        )
        total_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Carte 2 : Produits en alerte
        alert_card = self.create_stat_card(
            stats_frame,
            "Produits en alerte",
            "18",
            "#dc3545",
            "⚠️"
        )
        alert_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Carte 3 : Dernière mise à jour
        update_card = self.create_stat_card(
            stats_frame,
            "Dernière mise à jour",
            datetime.now().strftime("%H:%M"),
            "#198754",
            "🕒"
        )
        update_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        # Configurer les colonnes pour qu'elles s'étendent
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)

    def create_stat_card(self, parent, title, value, color, icon):
        """Crée une carte de statistique"""
        card = tk.Frame(parent, bg='white', bd=1, relief=tk.RIDGE)

        # Icône
        tk.Label(
            card,
            text=icon,
            font=('times new roman', 24),
            bg='white',
            fg=color
        ).pack(pady=(10, 0))

        # Valeur
        tk.Label(
            card,
            text=value,
            font=('times new roman', 22, 'bold'),
            bg='white',
            fg=color
        ).pack(pady=5)

        # Titre
        tk.Label(
            card,
            text=title,
            font=('times new roman', 10),
            bg='white',
            fg='#6c757d',
            wraplength=150
        ).pack(pady=(0, 10))

        return card

    # ===================== CONTENU PRINCIPAL =====================
    def create_main_content(self):
        main_content = tk.Frame(self, bg='#f5f6f8')
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Frame pour les deux sections (50/50)
        top_frame = tk.Frame(main_content, bg='#f5f6f8')
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Frame bas pour l'historique
        bottom_frame = tk.Frame(main_content, bg='#f5f6f8')
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # ===== ÉTAT DU STOCK (GAUCHE) =====
        stock_frame = tk.Frame(top_frame, bg='white', bd=2, relief=tk.RIDGE)
        stock_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Titre
        title_frame = tk.Frame(stock_frame, bg='#e9ecef')
        title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            title_frame,
            text='📋 État du stock',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Bouton refresh
        tk.Button(
            title_frame,
            text='🔄',
            font=('times new roman', 10, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            bd=0,
            width=3,
            command=self.load_stock_status
        ).pack(side=tk.RIGHT, padx=10, pady=5)

        # Treeview
        tree_frame = tk.Frame(stock_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.stock_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Nom', 'Catégorie', 'Quantité', 'Seuil min', 'Statut'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=12
        )

        v_scrollbar.config(command=self.stock_tree.yview)
        h_scrollbar.config(command=self.stock_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.stock_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        stock_columns = [
            ('ID', 'ID', 40),
            ('Nom', 'Produit', 120),
            ('Catégorie', 'Catégorie', 100),
            ('Quantité', 'Quantité', 70),
            ('Seuil min', 'Seuil min', 70),
            ('Statut', 'Statut', 70)
        ]

        for col, text, width in stock_columns:
            self.stock_tree.heading(col, text=text)
            self.stock_tree.column(col, width=width, anchor=tk.CENTER)

        # Tag pour les couleurs
        self.stock_tree.tag_configure('ok', background='#d4edda')
        self.stock_tree.tag_configure('alerte', background='#f8d7da')

        # ===== HISTORIQUE DES MOUVEMENTS (DROITE) =====
        history_frame = tk.Frame(top_frame, bg='white', bd=2, relief=tk.RIDGE)
        history_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Titre
        history_title_frame = tk.Frame(history_frame, bg='#e9ecef')
        history_title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            history_title_frame,
            text='📈 Historique des mouvements',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Filtre par période
        filter_frame = tk.Frame(history_title_frame, bg='#e9ecef')
        filter_frame.pack(side=tk.RIGHT, padx=10, pady=5)

        self.period_var = tk.StringVar(value='7j')
        periods = [('7j', '7 jours'), ('30j', '30 jours'), ('Tout', 'Tout voir')]

        for text, tooltip in periods:
            tk.Radiobutton(
                filter_frame,
                text=text,
                variable=self.period_var,
                value=text,
                bg='#e9ecef',
                font=('times new roman', 9),
                command=self.filter_history
            ).pack(side=tk.LEFT, padx=2)

        # Treeview historique
        history_tree_frame = tk.Frame(history_frame, bg='white')
        history_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        hist_v_scrollbar = tk.Scrollbar(history_tree_frame, orient=tk.VERTICAL)
        hist_h_scrollbar = tk.Scrollbar(history_tree_frame, orient=tk.HORIZONTAL)

        self.history_tree = ttk.Treeview(
            history_tree_frame,
            columns=('Date', 'Produit', 'Type', 'Quantité', 'Origine', 'Utilisateur'),
            show='headings',
            yscrollcommand=hist_v_scrollbar.set,
            xscrollcommand=hist_h_scrollbar.set,
            height=12
        )

        hist_v_scrollbar.config(command=self.history_tree.yview)
        hist_h_scrollbar.config(command=self.history_tree.xview)

        hist_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        hist_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        history_columns = [
            ('Date', 'Date/Heure', 120),
            ('Produit', 'Produit', 100),
            ('Type', 'Type', 70),
            ('Quantité', 'Quantité', 70),
            ('Origine', 'Origine', 100),
            ('Utilisateur', 'Utilisateur', 90)
        ]

        for col, text, width in history_columns:
            self.history_tree.heading(col, text=text)
            self.history_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags pour les types de mouvements
        self.history_tree.tag_configure('entree', foreground='#198754')
        self.history_tree.tag_configure('sortie', foreground='#dc3545')

        # ===== HISTORIQUE COMPLET (BAS) =====
        full_history_frame = tk.Frame(bottom_frame, bg='white', bd=2, relief=tk.RIDGE)
        full_history_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        full_title_frame = tk.Frame(full_history_frame, bg='#e9ecef')
        full_title_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            full_title_frame,
            text='📜 Historique complet récent',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        # Treeview historique complet
        full_tree_frame = tk.Frame(full_history_frame, bg='white')
        full_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        full_v_scrollbar = tk.Scrollbar(full_tree_frame, orient=tk.VERTICAL)
        full_h_scrollbar = tk.Scrollbar(full_tree_frame, orient=tk.HORIZONTAL)

        self.full_history_tree = ttk.Treeview(
            full_tree_frame,
            columns=('Date', 'Produit', 'Type', 'Quantité', 'Origine', 'Utilisateur'),
            show='headings',
            yscrollcommand=full_v_scrollbar.set,
            xscrollcommand=full_h_scrollbar.set,
            height=8
        )

        full_v_scrollbar.config(command=self.full_history_tree.yview)
        full_h_scrollbar.config(command=self.full_history_tree.xview)

        full_v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        full_h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.full_history_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes (identique)
        for col, text, width in history_columns:
            self.full_history_tree.heading(col, text=text)
            self.full_history_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags
        self.full_history_tree.tag_configure('entree', foreground='#198754')
        self.full_history_tree.tag_configure('sortie', foreground='#dc3545')

    # ===================== LOGIQUE =====================
    def load_stats(self):
        """Charge les statistiques"""
        # Données d'exemple
        total_articles = 1245
        produits_alerte = 18
        derniere_mise_a_jour = datetime.now().strftime("%d/%m %H:%M")

        # Vous remplaceriez cela par des appels à votre base de données
        print(f"Chargement des statistiques: {total_articles} articles, {produits_alerte} en alerte")

    def load_stock_status(self):
        """Charge l'état du stock"""
        self.stock_tree.delete(*self.stock_tree.get_children())

        # Données d'exemple
        produits_exemple = [
            (1, 'Coca-Cola 2L', 'Boissons', 45, 10, 'OK'),
            (2, 'Pain Blanc', 'Boulangerie', 5, 15, 'ALERTE'),
            (3, 'Lait Frais 1L', 'Produits Laitiers', 28, 20, 'OK'),
            (4, 'Eau Minérale 1.5L', 'Boissons', 120, 30, 'OK'),
            (5, 'Fromage 200g', 'Produits Laitiers', 3, 10, 'ALERTE'),
            (6, 'Jus d\'Orange 1L', 'Boissons', 8, 15, 'ALERTE'),
            (7, 'Croissant', 'Boulangerie', 40, 20, 'OK'),
            (8, 'Yaourt Nature', 'Produits Laitiers', 50, 15, 'OK'),
            (9, 'Pommes 1kg', 'Fruits', 35, 10, 'OK'),
            (10, 'Pâtes 500g', 'Épicerie', 60, 25, 'OK'),
            (11, 'Riz 1kg', 'Épicerie', 2, 10, 'ALERTE'),
            (12, 'Café 250g', 'Épicerie', 25, 5, 'OK'),
        ]

        for prod in produits_exemple:
            id_prod, nom, categorie, quantite, seuil, statut = prod
            tag = 'alerte' if statut == 'ALERTE' else 'ok'

            self.stock_tree.insert(
                '',
                tk.END,
                values=(id_prod, nom, categorie, quantite, seuil, statut),
                tags=(tag,)
            )

    def load_stock_history(self):
        """Charge l'historique des mouvements"""
        self.history_tree.delete(*self.history_tree.get_children())
        self.full_history_tree.delete(*self.full_history_tree.get_children())

        # Données d'exemple pour l'historique
        mouvements_exemple = [
            ('13/01 14:30', 'Coca-Cola 2L', 'Entrée', 50, 'Commande #450', 'Jean Dupont'),
            ('13/01 14:25', 'Pain Blanc', 'Sortie', 10, 'Vente #789', 'Marie Curie'),
            ('13/01 13:45', 'Lait Frais 1L', 'Sortie', 5, 'Vente #788', 'Pierre Martin'),
            ('13/01 12:30', 'Fromage 200g', 'Entrée', 20, 'Commande #449', 'Jean Dupont'),
            ('13/01 11:15', 'Jus d\'Orange 1L', 'Sortie', 8, 'Vente #787', 'Marie Curie'),
            ('12/01 16:20', 'Eau Minérale 1.5L', 'Entrée', 100, 'Commande #448', 'Jean Dupont'),
            ('12/01 15:10', 'Croissant', 'Sortie', 15, 'Vente #786', 'Pierre Martin'),
            ('12/01 14:05', 'Yaourt Nature', 'Sortie', 12, 'Vente #785', 'Marie Curie'),
            ('12/01 11:30', 'Pommes 1kg', 'Entrée', 40, 'Commande #447', 'Jean Dupont'),
            ('11/01 17:15', 'Pâtes 500g', 'Sortie', 25, 'Vente #784', 'Pierre Martin'),
        ]

        for i, mouvement in enumerate(mouvements_exemple):
            date, produit, type_mvt, quantite, origine, utilisateur = mouvement
            tag = 'entree' if type_mvt == 'Entrée' else 'sortie'

            # Historique filtré (premier treeview)
            if i < 5:  # Afficher seulement les 5 premiers dans l'historique
                self.history_tree.insert(
                    '',
                    tk.END,
                    values=(date, produit, type_mvt, quantite, origine, utilisateur),
                    tags=(tag,)
                )

            # Historique complet (deuxième treeview)
            self.full_history_tree.insert(
                '',
                tk.END,
                values=(date, produit, type_mvt, quantite, origine, utilisateur),
                tags=(tag,)
            )

    def filter_history(self):
        """Filtre l'historique selon la période sélectionnée"""
        periode = self.period_var.get()
        print(f"Filtrage de l'historique pour: {periode}")
        # Vous implémenteriez ici la logique de filtrage par période

    def refresh_all(self):
        """Rafraîchit toutes les données"""
        self.load_stats()
        self.load_stock_status()
        self.load_stock_history()