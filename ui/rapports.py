import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use('Agg')
from db.models import get_connection, get_cursor
import pandas as pd
from tkinter import font as tkfont


class RapportsFrame(tk.Frame):
    def __init__(self, parent, user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)

        self.user = user
        self.go_dashboard = go_dashboard
        self.create_title()
        self.create_tabs()

        # Charger les données initiales
        self.load_ventes_data()
        self.load_stock_data()
        self.load_produits_data()
        self.load_employes_data()
        self.load_achats_data()

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
            text='📈 Rapports & Statistiques',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== ONGLETS =====================
    def create_tabs(self):
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet 1: Ventes
        self.tab_ventes = tk.Frame(self.notebook, bg='#f5f6f8')
        self.notebook.add(self.tab_ventes, text='💰 Ventes')
        self.create_tab_ventes()

        # Onglet 2: Stock
        self.tab_stock = tk.Frame(self.notebook, bg='#f5f6f8')
        self.notebook.add(self.tab_stock, text='📦 Stock')
        self.create_tab_stock()

        # Onglet 3: Produits
        self.tab_produits = tk.Frame(self.notebook, bg='#f5f6f8')
        self.notebook.add(self.tab_produits, text='🏷️ Produits')
        self.create_tab_produits()

        # Onglet 4: Employés
        self.tab_employes = tk.Frame(self.notebook, bg='#f5f6f8')
        self.notebook.add(self.tab_employes, text='👥 Employés')
        self.create_tab_employes()

        # Onglet 5: Achats
        self.tab_achats = tk.Frame(self.notebook, bg='#f5f6f8')
        self.notebook.add(self.tab_achats, text='📋 Achats')
        self.create_tab_achats()

    # ===================== ONGLET 1: VENTES =====================
    def create_tab_ventes(self):
        # ===== STATISTIQUES DU HAUT =====
        stats_frame = tk.Frame(self.tab_ventes, bg='#f5f6f8')
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        # CA du jour
        self.ca_card = self.create_stat_card(
            stats_frame,
            "Chiffre d'affaires du jour",
            "0 €",
            "#198754",
            "💰"
        )
        self.ca_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Ventes du jour
        self.ventes_card = self.create_stat_card(
            stats_frame,
            "Ventes du jour",
            "0",
            "#0d6efd",
            "📊"
        )
        self.ventes_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Panier moyen
        self.panier_card = self.create_stat_card(
            stats_frame,
            "Panier moyen",
            "0 €",
            "#6f42c1",
            "🛒"
        )
        self.panier_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        # Évolution
        self.evolution_card = self.create_stat_card(
            stats_frame,
            "Évolution vs hier",
            "0 %",
            "#fd7e14",
            "📈"
        )
        self.evolution_card.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')

        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # ===== GRAPHIQUES =====
        graphs_frame = tk.Frame(self.tab_ventes, bg='#f5f6f8')
        graphs_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        # Graphique CA par heure
        hour_frame = tk.Frame(graphs_frame, bg='white', bd=2, relief=tk.RIDGE)
        hour_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        tk.Label(
            hour_frame,
            text=' CA par heure (aujourd\'hui)',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        self.hour_canvas_frame = tk.Frame(hour_frame, bg='white')
        self.hour_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Graphique CA 30 derniers jours
        days_frame = tk.Frame(graphs_frame, bg='white', bd=2, relief=tk.RIDGE)
        days_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        tk.Label(
            days_frame,
            text=' CA des 30 derniers jours',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        self.days_canvas_frame = tk.Frame(days_frame, bg='white')
        self.days_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ===== TABLEAU VENTES =====
        table_frame = tk.Frame(self.tab_ventes, bg='#f5f6f8')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

        # Titre + filtres
        header_frame = tk.Frame(table_frame, bg='white', bd=1, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            header_frame,
            text='📋 Dernières ventes',
            font=('times new roman', 12, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Filtre période
        tk.Label(
            header_frame,
            text='Période :',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.period_var = tk.StringVar(value='7j')
        periods = ['7 jours', '30 jours', 'Tout']
        period_menu = ttk.Combobox(
            header_frame,
            textvariable=self.period_var,
            values=periods,
            font=('times new roman', 10),
            width=12,
            state='readonly'
        )
        period_menu.pack(side=tk.LEFT, padx=5)
        period_menu.bind('<<ComboboxSelected>>', self.filter_ventes_table)

        # Bouton rafraîchir
        tk.Button(
            header_frame,
            text='🔄 Rafraîchir',
            font=('times new roman', 10),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.load_ventes_data
        ).pack(side=tk.RIGHT, padx=10, pady=5)

        # Tableau
        table_container = tk.Frame(table_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)

        self.ventes_tree = ttk.Treeview(
            table_container,
            columns=('ID', 'Date', 'Vendeur', 'Articles', 'Total', 'Panier moyen'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=8
        )

        v_scrollbar.config(command=self.ventes_tree.yview)
        h_scrollbar.config(command=self.ventes_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.ventes_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration colonnes
        ventes_columns = [
            ('ID', 'ID', 60),
            ('Date', 'Date/Heure', 120),
            ('Vendeur', 'Vendeur', 120),
            ('Articles', 'Articles', 80),
            ('Total', 'Total €', 100),
            ('Panier moyen', 'Panier moyen €', 100)
        ]

        for col, text, width in ventes_columns:
            self.ventes_tree.heading(col, text=text)
            self.ventes_tree.column(col, width=width, anchor=tk.CENTER)

    # ===================== ONGLET 2: STOCK =====================
    def create_tab_stock(self):
        # ===== STATISTIQUES =====
        stats_frame = tk.Frame(self.tab_stock, bg='#f5f6f8')
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        # Rupture
        self.rupture_card = self.create_stat_card(
            stats_frame,
            "Produits en rupture",
            "0",
            "#dc3545",
            "🛑"
        )
        self.rupture_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Alerte
        self.alerte_card = self.create_stat_card(
            stats_frame,
            "Produits en alerte",
            "0",
            "#fd7e14",
            "⚠️"
        )
        self.alerte_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Normal
        self.normal_card = self.create_stat_card(
            stats_frame,
            "Produits normaux",
            "0",
            "#198754",
            "✅"
        )
        self.normal_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        # Total
        self.total_card_stock = self.create_stat_card(
            stats_frame,
            "Total produits",
            "0",
            "#0d6efd",
            "📦"
        )
        self.total_card_stock.grid(row=0, column=3, padx=5, pady=5, sticky='nsew')

        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)

        # ===== TABLEAU ÉTAT STOCK =====
        table_frame = tk.Frame(self.tab_stock, bg='#f5f6f8')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

        # Titre + filtres
        header_frame = tk.Frame(table_frame, bg='white', bd=1, relief=tk.RIDGE)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        tk.Label(
            header_frame,
            text='📊 État du stock',
            font=('times new roman', 12, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Filtre catégorie
        tk.Label(
            header_frame,
            text='Catégorie :',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.categorie_filter = ttk.Combobox(
            header_frame,
            font=('times new roman', 10),
            width=15,
            state='readonly'
        )
        self.categorie_filter.pack(side=tk.LEFT, padx=5)
        self.categorie_filter.set('Toutes')
        self.categorie_filter.bind('<<ComboboxSelected>>', self.filter_stock_table)

        # Filtre état
        tk.Label(
            header_frame,
            text='État :',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.etat_filter = ttk.Combobox(
            header_frame,
            values=['Tous', 'RUPTURE', 'ALERTE', 'NORMAL'],
            font=('times new roman', 10),
            width=12,
            state='readonly'
        )
        self.etat_filter.pack(side=tk.LEFT, padx=5)
        self.etat_filter.set('Tous')
        self.etat_filter.bind('<<ComboboxSelected>>', self.filter_stock_table)

        # Tableau
        table_container = tk.Frame(table_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)

        self.stock_tree = ttk.Treeview(
            table_container,
            columns=('Produit', 'Catégorie', 'Stock', 'Seuil', 'État'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=15
        )

        v_scrollbar.config(command=self.stock_tree.yview)
        h_scrollbar.config(command=self.stock_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.stock_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration colonnes avec tags
        stock_columns = [
            ('Produit', 'Produit', 200),
            ('Catégorie', 'Catégorie', 120),
            ('Stock', 'Stock', 80),
            ('Seuil', 'Seuil min', 80),
            ('État', 'État', 80)
        ]

        for col, text, width in stock_columns:
            self.stock_tree.heading(col, text=text)
            self.stock_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags pour couleurs
        self.stock_tree.tag_configure('RUPTURE', background='#f8d7da', foreground='#721c24')
        self.stock_tree.tag_configure('ALERTE', background='#fff3cd', foreground='#856404')
        self.stock_tree.tag_configure('NORMAL', background='#d4edda', foreground='#155724')

    # ===================== ONGLET 3: PRODUITS =====================
    def create_tab_produits(self):
        # ===== TOP 10 PRODUITS =====
        top_frame = tk.Frame(self.tab_produits, bg='#f5f6f8')
        top_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Titre
        tk.Label(
            top_frame,
            text='🏆 Top 10 produits par chiffre d\'affaires',
            font=('times new roman', 14, 'bold'),
            bg='#f5f6f8',
            fg='#0f4d7d'
        ).pack(anchor='w', pady=(0, 10))

        # Tableau
        table_container = tk.Frame(top_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)

        self.produits_tree = ttk.Treeview(
            table_container,
            columns=('Rang', 'Produit', 'Catégorie', 'Qté vendue', 'CA €', 'Prix moyen'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=12
        )

        v_scrollbar.config(command=self.produits_tree.yview)
        h_scrollbar.config(command=self.produits_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.produits_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration colonnes
        produits_columns = [
            ('Rang', '#', 50),
            ('Produit', 'Produit', 180),
            ('Catégorie', 'Catégorie', 120),
            ('Qté vendue', 'Qté vendue', 100),
            ('CA €', 'Chiffre d\'affaires', 120),
            ('Prix moyen', 'Prix moyen €', 100)
        ]

        for col, text, width in produits_columns:
            self.produits_tree.heading(col, text=text)
            self.produits_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags pour le top 3
        self.produits_tree.tag_configure('gold', background='#fff3cd')
        self.produits_tree.tag_configure('silver', background='#e9ecef')
        self.produits_tree.tag_configure('bronze', background='#f8d7da')

        # ===== CA PAR CATÉGORIE =====
        categ_frame = tk.Frame(self.tab_produits, bg='#f5f6f8')
        categ_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        tk.Label(
            categ_frame,
            text='📊 Répartition CA par catégorie',
            font=('times new roman', 12, 'bold'),
            bg='#f5f6f8'
        ).pack(anchor='w', pady=(10, 5))

        self.categ_canvas_frame = tk.Frame(categ_frame, bg='white', bd=2, relief=tk.RIDGE)
        self.categ_canvas_frame.pack(fill=tk.BOTH, expand=True)

    # ===================== ONGLET 4: EMPLOYÉS =====================
    def create_tab_employes(self):
        # ===== TABLEAU PERFORMANCE =====
        table_frame = tk.Frame(self.tab_employes, bg='#f5f6f8')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Titre
        tk.Label(
            table_frame,
            text='👥 Performance des vendeurs',
            font=('times new roman', 14, 'bold'),
            bg='#f5f6f8',
            fg='#0f4d7d'
        ).pack(anchor='w', pady=(0, 10))

        # Tableau
        table_container = tk.Frame(table_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)

        self.employes_tree = ttk.Treeview(
            table_container,
            columns=('Rang', 'Employé', 'Rôle', 'Ventes', 'Articles', 'CA €', 'Panier moyen'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=12
        )

        v_scrollbar.config(command=self.employes_tree.yview)
        h_scrollbar.config(command=self.employes_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.employes_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration colonnes
        employes_columns = [
            ('Rang', '#', 50),
            ('Employé', 'Employé', 150),
            ('Rôle', 'Rôle', 100),
            ('Ventes', 'Nb ventes', 80),
            ('Articles', 'Articles vendus', 100),
            ('CA €', 'Chiffre d\'affaires', 120),
            ('Panier moyen', 'Panier moyen €', 100)
        ]

        for col, text, width in employes_columns:
            self.employes_tree.heading(col, text=text)
            self.employes_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags pour les meilleurs vendeurs
        self.employes_tree.tag_configure('top1', background='#fff3cd', font=('times new roman', 10, 'bold'))
        self.employes_tree.tag_configure('top3', background='#e9ecef')

    # ===================== ONGLET 5: ACHATS =====================
    def create_tab_achats(self):
        # ===== STATISTIQUES =====
        stats_frame = tk.Frame(self.tab_achats, bg='#f5f6f8')
        stats_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

        # Commandes en attente
        self.attente_card = self.create_stat_card(
            stats_frame,
            "Commandes en attente",
            "0",
            "#fd7e14",
            "⏳"
        )
        self.attente_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Produits à réappro
        self.reappro_card = self.create_stat_card(
            stats_frame,
            "Produits à réappro",
            "0",
            "#dc3545",
            "⚠️"
        )
        self.reappro_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        # Budget engagé
        self.budget_card = self.create_stat_card(
            stats_frame,
            "Budget engagé",
            "0 €",
            "#0d6efd",
            "💰"
        )
        self.budget_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')

        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)

        # ===== TABLEAU BESOINS RÉAPPRO =====
        table_frame = tk.Frame(self.tab_achats, bg='#f5f6f8')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))

        # Titre
        tk.Label(
            table_frame,
            text='📋 Besoins en réapprovisionnement',
            font=('times new roman', 12, 'bold'),
            bg='#f5f6f8'
        ).pack(anchor='w', pady=(0, 5))

        # Tableau
        table_container = tk.Frame(table_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_container.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)

        self.achats_tree = ttk.Treeview(
            table_container,
            columns=('Produit', 'Stock actuel', 'Seuil min', 'À commander', 'Fournisseur'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=12
        )

        v_scrollbar.config(command=self.achats_tree.yview)
        h_scrollbar.config(command=self.achats_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.achats_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration colonnes
        achats_columns = [
            ('Produit', 'Produit', 200),
            ('Stock actuel', 'Stock actuel', 100),
            ('Seuil min', 'Seuil min', 80),
            ('À commander', 'À commander', 100),
            ('Fournisseur', 'Fournisseur', 150)
        ]

        for col, text, width in achats_columns:
            self.achats_tree.heading(col, text=text)
            self.achats_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags urgence
        self.achats_tree.tag_configure('URGENT', background='#f8d7da', font=('times new roman', 10, 'bold'))
        self.achats_tree.tag_configure('MOYEN', background='#fff3cd')

    # ===================== COMPOSANTS RÉUTILISABLES =====================
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
        value_label = tk.Label(
            card,
            text=value,
            font=('times new roman', 22, 'bold'),
            bg='white',
            fg=color
        )
        value_label.pack(pady=5)

        # Titre
        tk.Label(
            card,
            text=title,
            font=('times new roman', 10),
            bg='white',
            fg='#6c757d',
            wraplength=150
        ).pack(pady=(0, 10))

        # ⭐⭐ CORRECTION : Stocker la référence correctement ⭐⭐
        card.value_widget = value_label  # Utilisez value_widget au lieu de value_label
        return card
    # ===================== CHARGEMENT DES DONNÉES =====================
    def load_ventes_data(self):
        """Charge les données des ventes"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)

        try:
            # 1. Statistiques générales
            cur.execute("""
                SELECT 
                    COALESCE(SUM(total_vente), 0) as ca_jour,
                    COUNT(*) as nb_ventes_jour,
                    CASE 
                        WHEN COUNT(*) > 0 THEN ROUND(SUM(total_vente) / COUNT(*), 2)
                        ELSE 0 
                    END as panier_moyen
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
            """)

            stats = cur.fetchone()

            if stats:
                # Mettre à jour les cartes
                self.update_card_value(self.ca_card, f"{stats['ca_jour']:,.2f} €")
                self.update_card_value(self.ventes_card, str(stats['nb_ventes_jour']))
                self.update_card_value(self.panier_card, f"{stats['panier_moyen']:.2f} €")

            # 2. Évolution vs hier
            cur.execute("""
                WITH ca_aujourdhui AS (
                    SELECT COALESCE(SUM(total_vente), 0) as ca
                    FROM vente 
                    WHERE DATE(date_vente) = CURRENT_DATE
                ),
                ca_hier AS (
                    SELECT COALESCE(SUM(total_vente), 0) as ca
                    FROM vente 
                    WHERE DATE(date_vente) = CURRENT_DATE - 1
                )
                SELECT 
                    CASE 
                        WHEN ca_hier.ca > 0 
                        THEN ROUND((ca_aujourdhui.ca - ca_hier.ca) / ca_hier.ca * 100, 1)
                        ELSE 0 
                    END as evolution
                FROM ca_aujourdhui, ca_hier
            """)

            evolution = cur.fetchone()
            if evolution:
                evol_text = f"{evolution['evolution']:+.1f} %"
                color = '#198754' if evolution['evolution'] >= 0 else '#dc3545'
                if hasattr(self.evolution_card, 'value_widget'):  # ⬅️ VÉRIFIER L'EXISTENCE
                    self.evolution_card.value_widget.config(text=evol_text, fg=color)

            # 3. Tableau des ventes récentes
            self.ventes_tree.delete(*self.ventes_tree.get_children())

            cur.execute("""
                SELECT 
                    v.id_vente,
                    v.date_vente,
                    u.nom as vendeur,
                    SUM(lv.quantite_vendue) as articles,
                    v.total_vente,
                    CASE 
                        WHEN COUNT(lv.id_vente) > 0 
                        THEN ROUND(v.total_vente / COUNT(DISTINCT lv.id_produit), 2)
                        ELSE 0 
                    END as panier_moyen
                FROM vente v
                JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
                JOIN ligne_vente lv ON v.id_vente = lv.id_vente
                WHERE v.date_vente >= CURRENT_DATE - INTERVAL '30 days'
                GROUP BY v.id_vente, v.date_vente, u.nom, v.total_vente
                ORDER BY v.date_vente DESC
                LIMIT 50
            """)

            ventes = cur.fetchall()

            for vente in ventes:
                date_str = vente['date_vente'].strftime("%d/%m %H:%M")
                self.ventes_tree.insert(
                    '',
                    tk.END,
                    values=(
                        vente['id_vente'],
                        date_str,
                        vente['vendeur'],
                        vente['articles'],
                        f"{vente['total_vente']:.2f}",
                        f"{vente['panier_moyen']:.2f}"
                    )
                )

            # 4. Graphique CA par heure
            cur.execute("SELECT * FROM vue_ca_par_heure ORDER BY heure")
            ca_par_heure = cur.fetchall()
            self.create_hour_chart(ca_par_heure)

            # 5. Graphique CA 30 derniers jours
            cur.execute("SELECT * FROM vue_ca_30_derniers_jours ORDER BY date")
            ca_30_jours = cur.fetchall()
            self.create_days_chart(ca_30_jours)

        except Exception as e:
            print(f"Erreur load_ventes_data: {e}")
        finally:
            cur.close()
            conn.close()

    def load_stock_data(self):
        """Charge les données du stock"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)

        try:
            # 1. Statistiques
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN etat = 'RUPTURE' THEN 1 ELSE 0 END) as rupture,
                    SUM(CASE WHEN etat = 'ALERTE' THEN 1 ELSE 0 END) as alerte,
                    SUM(CASE WHEN etat = 'NORMAL' THEN 1 ELSE 0 END) as normal
                FROM vue_etat_stock
            """)

            stats = cur.fetchone()

            if stats:
                self.update_card_value(self.rupture_card, str(stats['rupture']))
                self.update_card_value(self.alerte_card, str(stats['alerte']))
                self.update_card_value(self.normal_card, str(stats['normal']))
                self.update_card_value(self.total_card_stock, str(stats['total']))

            # 2. Charger les catégories pour le filtre
            cur.execute("SELECT DISTINCT categorie FROM vue_etat_stock ORDER BY categorie")
            categories = ['Toutes'] + [row['categorie'] for row in cur.fetchall()]
            self.categorie_filter['values'] = categories

            # 3. Tableau état stock - UTILISEZ quantite_stock COMME DANS VOTRE VUE
            self.stock_tree.delete(*self.stock_tree.get_children())

            cur.execute("SELECT * FROM vue_etat_stock ORDER BY etat, quantite_stock")  # ⬅️ CORRIGÉ
            produits = cur.fetchall()

            for prod in produits:
                tag = prod['etat']
                self.stock_tree.insert(
                    '',
                    tk.END,
                    values=(
                        prod['nom'],
                        prod['categorie'],
                        prod['quantite_stock'],  # ⬅️ CORRIGÉ
                        prod['seuil_min'],
                        prod['etat']
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            print(f"Erreur load_stock_data: {e}")
        finally:
            cur.close()
            conn.close()

    def load_produits_data(self):
        """Charge les données des produits"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)

        try:
            # 1. Top 10 produits
            self.produits_tree.delete(*self.produits_tree.get_children())

            cur.execute("SELECT * FROM vue_top_produits ORDER BY chiffre_affaires DESC LIMIT 10")
            top_produits = cur.fetchall()

            for i, prod in enumerate(top_produits, 1):
                tag = ''
                if i == 1:
                    tag = 'gold'
                elif i == 2:
                    tag = 'silver'
                elif i == 3:
                    tag = 'bronze'

                # UTILISEZ marge_unitaire AU LIEU DE prix_moyen_vente
                self.produits_tree.insert(
                    '',
                    tk.END,
                    values=(
                        i,
                        prod['nom'],
                        prod['categorie'],
                        prod['quantite_vendue'],
                        f"{prod['chiffre_affaires']:,.2f}",
                        f"{prod['marge_unitaire']:.2f}"  # ⬅️ CORRIGÉ
                    ),
                    tags=(tag,)
                )

            # 2. Graphique CA par catégorie - UTILISEZ LES BONS NOMS
            cur.execute("SELECT * FROM vue_ca_par_categorie ORDER BY chiffre_affaires DESC")
            ca_categories = cur.fetchall()
            self.create_categories_chart(ca_categories)

        except Exception as e:
            print(f"Erreur load_produits_data: {e}")
        finally:
            cur.close()
            conn.close()

    def load_employes_data(self):
        """Charge les données des employés"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)

        try:
            self.employes_tree.delete(*self.employes_tree.get_children())

            cur.execute("""
                SELECT * FROM vue_performance_vendeurs 
                WHERE role IN ('CAISSIER', 'ADMIN')
                ORDER BY chiffre_affaires DESC
            """)

            employes = cur.fetchall()

            for i, emp in enumerate(employes, 1):
                tag = 'top1' if i == 1 else ('top3' if i <= 3 else '')

                self.employes_tree.insert(
                    '',
                    tk.END,
                    values=(
                        i,
                        emp['nom'],
                        emp['role'],
                        emp['nb_ventes'],
                        emp['articles_vendus'],
                        f"{emp['chiffre_affaires']:,.2f}",
                        f"{emp['panier_moyen']:.2f}"
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            print(f"Erreur load_employes_data: {e}")
        finally:
            cur.close()
            conn.close()

    def load_achats_data(self):
        """Charge les données des achats"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)

        try:
            # 1. Statistiques - CORRIGEZ LA REQUÊTE
            # Compter les produits distincts seulement (pas les commandes)
            cur.execute("""
                SELECT COUNT(DISTINCT produit) as produits_reappro
                FROM vue_besoin_reappro
            """)

            stats = cur.fetchone()

            if stats:
                # Pour les commandes en attente, on va chercher dans commande_achat
                cur.execute("SELECT COUNT(*) as commandes_attente FROM commande_achat WHERE statut = 'EN_COURS'")
                commandes = cur.fetchone()

                self.update_card_value(self.attente_card, str(commandes['commandes_attente']))
                self.update_card_value(self.reappro_card, str(stats['produits_reappro']))

            # Budget engagé (commandes en cours)
            cur.execute("""
                SELECT COALESCE(SUM(lca.quantite_commandee * lca.prix_unitaire), 0) as budget
                FROM commande_achat ca
                JOIN ligne_commande_achat lca ON ca.id_commande_achat = lca.id_commande_achat
                WHERE ca.statut = 'EN_COURS'
            """)

            budget = cur.fetchone()
            if budget:
                self.update_card_value(self.budget_card, f"{budget['budget']:,.2f} €")

            # 2. Tableau besoins réappro
            self.achats_tree.delete(*self.achats_tree.get_children())

            cur.execute("SELECT * FROM vue_besoin_reappro ORDER BY quantite_stock")
            besoins = cur.fetchall()

            for besoin in besoins:
                # UTILISEZ LES NOMS EXACTS
                stock = besoin['quantite_stock']
                seuil = besoin['seuil_min']
                a_commander = besoin['quantite_suggeree']
                fournisseur = besoin['fournisseur_principal']

                tag = 'URGENT' if stock <= 0 else ('MOYEN' if stock <= seuil else '')

                self.achats_tree.insert(
                    '',
                    tk.END,
                    values=(
                        besoin['produit'],
                        stock,
                        seuil,
                        max(0, a_commander),
                        fournisseur
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            print(f"Erreur load_achats_data: {e}")
        finally:
            cur.close()
            conn.close()

    # ===================== GRAPHIQUES =====================
    def create_hour_chart(self, data):
        """Crée le graphique CA par heure"""
        # Nettoyer le frame précédent
        for widget in self.hour_canvas_frame.winfo_children():
            widget.destroy()

        if not data:
            tk.Label(
                self.hour_canvas_frame,
                text="Aucune donnée aujourd'hui",
                font=('times new roman', 11),
                fg='#6c757d',
                bg='white'
            ).pack(expand=True)
            return

        # Préparer les données
        heures = [str(int(row['heure'])) for row in data]
        ca = [float(row['chiffre_affaires']) for row in data]

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(6, 3), dpi=80)
        bars = ax.bar(heures, ca, color='#0d6efd', alpha=0.7)

        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                        f'{height:.0f}€', ha='center', va='bottom', fontsize=8)

        ax.set_xlabel('Heure', fontsize=9)
        ax.set_ylabel('CA (€)', fontsize=9)
        ax.set_title('CA par heure', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, self.hour_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_days_chart(self, data):
        """Crée le graphique CA 30 derniers jours"""
        for widget in self.days_canvas_frame.winfo_children():
            widget.destroy()

        if not data:
            tk.Label(
                self.days_canvas_frame,
                text="Aucune donnée disponible",
                font=('times new roman', 11),
                fg='#6c757d',
                bg='white'
            ).pack(expand=True)
            return

        # Préparer les données
        dates = [row['date'].strftime("%d/%m") for row in data]
        ca = [float(row['chiffre_affaires']) for row in data]

        # Créer le graphique
        fig, ax = plt.subplots(figsize=(6, 3), dpi=80)
        ax.plot(dates, ca, color='#198754', linewidth=2, marker='o', markersize=4)

        ax.set_xlabel('Date', fontsize=9)
        ax.set_ylabel('CA (€)', fontsize=9)
        ax.set_title('CA 30 derniers jours', fontsize=10, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Rotation des dates pour lisibilité
        plt.xticks(rotation=45, fontsize=7)
        plt.tight_layout()

        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, self.days_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_categories_chart(self, data):
        """Crée le graphique CA par catégorie"""
        for widget in self.categ_canvas_frame.winfo_children():
            widget.destroy()

        if not data:
            tk.Label(
                self.categ_canvas_frame,
                text="Aucune donnée disponible",
                font=('times new roman', 11),
                fg='#6c757d',
                bg='white'
            ).pack(expand=True)
            return

        # ⭐⭐ CORRECTION : Utiliser les bons noms de colonnes ⭐⭐
        categories = [row['categorie'][:15] for row in data]  # 'categorie' pas 'Categorie'
        ca = [float(row['chiffre_affaires']) for row in data]

        # Palette
        try:
            colors = plt.cm.tab20c(range(len(categories)))
        except:
            import numpy as np
            colors = plt.cm.viridis(np.linspace(0, 1, len(categories)))

        # Créer le graphique
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=80)

        # Camembert
        ax1.pie(ca, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Répartition CA', fontsize=10, fontweight='bold')

        # Barres horizontales
        y_pos = range(len(categories))
        ax2.barh(y_pos, ca, color=colors)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(categories, fontsize=8)
        ax2.set_xlabel('CA (€)', fontsize=9)
        ax2.set_title('CA par catégorie', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.categ_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ===================== FONCTIONS UTILITAIRES =====================
    def update_card_value(self, card, value):
        """Met à jour la valeur d'une carte de statistique"""
        if hasattr(card, 'value_widget'):  # ⬅️ CORRIGÉ
            card.value_widget.config(text=value)



    def filter_ventes_table(self, event=None):
        """Filtre le tableau des ventes"""
        periode = self.period_var.get()

        # Calculer la date limite
        if periode == '7 jours':
            limit = datetime.now() - timedelta(days=7)
        elif periode == '30 jours':
            limit = datetime.now() - timedelta(days=30)
        else:  # Tout
            return

        # Filtrer les lignes
        for item in self.ventes_tree.get_children():
            values = self.ventes_tree.item(item, 'values')
            if values and len(values) > 1:
                date_str = values[1]
                try:
                    date_obj = datetime.strptime(date_str, "%d/%m %H:%M")
                    if date_obj >= limit:
                        self.ventes_tree.item(item, tags=())
                    else:
                        self.ventes_tree.detach(item)
                except:
                    pass

    def filter_stock_table(self, event=None):
        """Filtre le tableau du stock"""
        categorie = self.categorie_filter.get()
        etat = self.etat_filter.get()

        # Cacher toutes les lignes
        for item in self.stock_tree.get_children():
            self.stock_tree.item(item, tags=())

        # Montrer seulement celles qui correspondent
        for item in self.stock_tree.get_children():
            values = self.stock_tree.item(item, 'values')

            categorie_match = (categorie == 'Toutes') or (values[1] == categorie)
            etat_match = (etat == 'Tous') or (values[4] == etat)

            if categorie_match and etat_match:
                self.stock_tree.item(item, tags=(values[4],))
            else:
                self.stock_tree.detach(item)

    def refresh_all(self):
        """Rafraîchit toutes les données"""
        self.load_ventes_data()
        self.load_stock_data()
        self.load_produits_data()
        self.load_employes_data()
        self.load_achats_data()
