import tkinter as tk
from tkinter import ttk
from db.models import get_connection, get_cursor


class DashboardFrame(tk.Frame):
    def __init__(self, parent, user=None, go_dashboard=None):
        super().__init__(parent, bg='#e9ecef')
        self.pack(fill=tk.BOTH, expand=True)

        self.user = user
        self.go_dashboard = go_dashboard
        self.kpi_values = {}  # Pour stocker les labels des valeurs KPI

        self.create_title()
        self.create_kpis()
        self.create_charts()
        self.create_quick_actions()

        # Charger les données depuis la base
        self.load_dashboard_data()
        self.load_charts_data()

    # ===================== TITRE =====================
    def create_title(self):
        tk.Label(
            self,
            text="Dashboard",
            font=('times new roman', 18, 'bold'),
            bg='#e9ecef',
            fg='#212529'
        ).place(x=20, y=20)

    # ===================== KPI =====================
    def create_kpis(self):
        container = tk.Frame(self, bg='#e9ecef')
        container.place(x=20, y=70, width=1030, height=120)

        # Créer les KPIs et stocker les références
        self.create_kpi(container, 0, "Chiffre d'affaires du jour", "0", "ca_jour")
        self.create_kpi(container, 260, "Nombre de ventes du jour", "0", "ventes_jour")
        self.create_kpi(container, 520, "Produits en seuil bas", "0", "alertes_stock")
        self.create_kpi(container, 780, "Nombre total de produits", "0", "total_produits")

    def create_kpi(self, parent, x, title, value, key):
        frame = tk.Frame(
            parent,
            bg='white',
            highlightbackground='#ced4da',
            highlightthickness=1
        )
        frame.place(x=x, y=0, width=240, height=100)

        # configuration grid interne
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=2)
        frame.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(
            frame,
            text=title,
            font=('times new roman', 14, 'bold'),
            bg='white',
            fg='#6c757d',
            wraplength=210,
            justify='left'
        )
        title_label.grid(row=0, column=0, sticky='w', padx=15, pady=(10, 0))

        value_label = tk.Label(
            frame,
            text=value,
            font=('times new roman', 22, 'bold'),
            bg='white',
            fg='#212529'
        )
        value_label.grid(row=1, column=0, sticky='w', padx=15, pady=(0, 10))

        # Stocker la référence pour mise à jour
        self.kpi_values[key] = value_label

    # ===================== ZONES GRAPHIQUES =====================
    def create_charts(self):
        container = tk.Frame(self, bg='#f5f6f8')
        container.place(x=20, y=210, width=1030, height=260)

        # Graphique gauche: Top 5 produits
        self.left_chart_frame = tk.Frame(
            container,
            bg='white',
            highlightbackground='#ced4da',
            highlightthickness=1
        )
        self.left_chart_frame.place(x=0, y=0, width=500, height=260)

        # Titre graphique gauche
        tk.Label(
            self.left_chart_frame,
            text="📊 Top 5 produits vendus (30 jours)",
            font=('times new roman', 15, 'bold'),
            bg='#d3d3d3',
            fg='#212529',
            anchor='w',
            padx=10
        ).place(x=0, y=0, relwidth=1, height=40)

        # Zone pour le tableau des top produits
        self.top_products_tree = ttk.Treeview(
            self.left_chart_frame,
            columns=('Produit', 'Quantité vendue'),
            show='headings',
            height=8
        )
        self.top_products_tree.place(x=10, y=50, width=480, height=200)

        # Configuration des colonnes
        self.top_products_tree.heading('Produit', text='Produit')
        self.top_products_tree.heading('Quantité vendue', text='Qté vendue')
        self.top_products_tree.column('Produit', width=320, anchor='w')
        self.top_products_tree.column('Quantité vendue', width=140, anchor='center')

        # Graphique droit: Dernières ventes
        self.right_chart_frame = tk.Frame(
            container,
            bg='white',
            highlightbackground='#ced4da',
            highlightthickness=1
        )
        self.right_chart_frame.place(x=530, y=0, width=500, height=260)

        # Titre graphique droit
        tk.Label(
            self.right_chart_frame,
            text="💰 Dernières ventes",
            font=('times new roman', 15, 'bold'),
            bg='#d3d3d3',
            fg='#212529',
            anchor='w',
            padx=10
        ).place(x=0, y=0, relwidth=1, height=40)

        # Zone pour le tableau des dernières ventes
        self.recent_sales_tree = ttk.Treeview(
            self.right_chart_frame,
            columns=('ID', 'Vendeur', 'Heure', 'Montant'),
            show='headings',
            height=8
        )
        self.recent_sales_tree.place(x=10, y=50, width=480, height=200)

        # Configuration des colonnes
        self.recent_sales_tree.heading('ID', text='N°')
        self.recent_sales_tree.heading('Vendeur', text='Vendeur')
        self.recent_sales_tree.heading('Heure', text='Heure')
        self.recent_sales_tree.heading('Montant', text='Montant')
        self.recent_sales_tree.column('ID', width=50, anchor='center')
        self.recent_sales_tree.column('Vendeur', width=150, anchor='w')
        self.recent_sales_tree.column('Heure', width=100, anchor='center')
        self.recent_sales_tree.column('Montant', width=150, anchor='center')

    # ===================== ACCÈS RAPIDE =====================
    def create_quick_actions(self):
        frame = tk.Frame(
            self,
            bg='white',
            highlightbackground='#ced4da',
            highlightthickness=1
        )
        frame.place(x=20, y=490, width=1030, height=55)

        tk.Label(
            frame,
            text="Accès rapide",
            font=('times new roman', 11, 'bold'),
            bg='white'
        ).place(x=10, y=5)

        role = self.user['role']
        
        # Helper pour créer un bouton
        def add_btn(text, color, x_pos, command):
            tk.Button(
                frame,
                text=text,
                bg=color,
                fg='white',
                font=('times new roman', 13, 'bold'),
                bd=0,
                padx=15,
                cursor='hand2',
                command=command
            ).place(x=x_pos, y=15)

        # Logique selon le rôle
        if role == 'ADMIN':
            add_btn("Ajouter un produit", '#0d6efd', 120, self.go_to_produits)
            add_btn("Passer une vente", '#198754', 360, self.go_to_ventes)
            add_btn("Voir rapports", '#343a40', 600, self.go_to_rapports)

        elif role == 'CAISSIER':
            add_btn("Passer une vente", '#198754', 120, self.go_to_ventes)
            add_btn("Mes Reçus", '#6c757d', 360, self.go_to_recus)
        
        elif role == 'GESTIONNAIRE_STOCK':
             add_btn("Ajouter un produit", '#0d6efd', 120, self.go_to_produits)
             add_btn("Gérer Catégories", '#6610f2', 360, self.go_to_categories)
             add_btn("Voir Stock", '#fd7e14', 600, self.go_to_stock)
        
        elif role == 'RESPONSABLE_ACHAT':
            add_btn("Fournisseurs", '#0d6efd', 120, self.go_to_fournisseurs)
            add_btn("Commandes", '#198754', 360, self.go_to_commandes)

    # ===================== CHARGEMENT DES DONNÉES =====================
    def load_dashboard_data(self):
        """Charge les données du dashboard depuis la base"""
        try:
            conn = get_connection()
            if conn is None:
                print("Erreur: Impossible de se connecter à la base de données")
                return

            cur = get_cursor(conn)
            
            is_admin = (self.user['role'] == 'ADMIN')
            user_id = self.user['id_utilisateur']

            # 1. Chiffre d'affaires du jour
            query_ca = """
                SELECT COALESCE(SUM(total_vente), 0) as ca_jour
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
            """
            params_ca = []
            
            if not is_admin:
                query_ca += " AND id_utilisateur = %s"
                params_ca.append(user_id)
            
            cur.execute(query_ca, tuple(params_ca))
            ca_result = cur.fetchone()
            if ca_result:
                self.update_kpi('ca_jour', f"{ca_result['ca_jour']:,.2f} FCFA")

            # 2. Nombre de ventes du jour
            query_nb = """
                SELECT COUNT(*) as ventes_jour
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
            """
            params_nb = []
            
            if not is_admin:
                query_nb += " AND id_utilisateur = %s"
                params_nb.append(user_id)

            cur.execute(query_nb, tuple(params_nb))
            ventes_result = cur.fetchone()
            if ventes_result:
                self.update_kpi('ventes_jour', str(ventes_result['ventes_jour']))

            # 3. Produits en seuil bas (GLOBAL)
            try:
                cur.execute("""
                    SELECT COUNT(*) as alertes
                    FROM vue_etat_stock 
                    WHERE etat IN ('RUPTURE', 'ALERTE')
                """)
            except:
                cur.execute("""
                    SELECT COUNT(*) as alertes
                    FROM produit p
                    JOIN categorie c ON p.id_categorie = c.id_categorie
                    WHERE p.quantite_stock <= COALESCE(p.seuil_min_personnalise, c.seuil_min_defaut)
                    AND p.statut = 'ACTIF'
                """)

            alertes_result = cur.fetchone()
            if alertes_result:
                self.update_kpi('alertes_stock', str(alertes_result['alertes']))

            # 4. Nombre total de produits actifs (GLOBAL)
            cur.execute("""
                SELECT COUNT(*) as total
                FROM produit 
                WHERE statut = 'ACTIF'
            """)
            total_result = cur.fetchone()
            if total_result:
                self.update_kpi('total_produits', str(total_result['total']))

            cur.close()
            conn.close()

        except Exception as e:
            print(f"Erreur lors du chargement des données dashboard: {e}")

    def load_charts_data(self):
        """Charge les données pour les graphiques/tableaux"""
        try:
            conn = get_connection()
            if conn is None:
                return

            cur = get_cursor(conn)
            
            is_admin = (self.user['role'] == 'ADMIN')
            user_id = self.user['id_utilisateur']

            # 1. TOP 5 PRODUITS VENDUS (30 derniers jours)
            self.top_products_tree.delete(*self.top_products_tree.get_children())

            query_top = """
                SELECT 
                    p.nom_produit as nom,
                    COALESCE(SUM(lv.quantite_vendue), 0) as quantite_vendue
                FROM produit p
                LEFT JOIN ligne_vente lv ON p.id_produit = lv.id_produit
                LEFT JOIN vente v ON lv.id_vente = v.id_vente
                WHERE (v.date_vente >= CURRENT_DATE - INTERVAL '30 days' OR v.date_vente IS NULL)
            """
            params_top = []
            
            if not is_admin:
                query_top += " AND v.id_utilisateur = %s"
                params_top.append(user_id)
            
            query_top += """
                GROUP BY p.id_produit, p.nom_produit
                ORDER BY quantite_vendue DESC
                LIMIT 5
            """
            
            # Si Admin et si vue existe, on pourrait optimiser, mais la query manuelle est sûre.
            cur.execute(query_top, tuple(params_top))
            top_products = cur.fetchall()

            for i, product in enumerate(top_products, 1):
                prefix = ""
                if i == 1: prefix = "🥇 "
                elif i == 2: prefix = "🥈 "
                elif i == 3: prefix = "🥉 "

                self.top_products_tree.insert(
                    '',
                    tk.END,
                    values=(
                        f"{prefix}{product['nom']}",
                        product['quantite_vendue']
                    )
                )

            # 2. DERNIÈRES VENTES (5 dernières ventes du jour)
            self.recent_sales_tree.delete(*self.recent_sales_tree.get_children())

            query_recent = """
                SELECT 
                    v.id_vente,
                    TO_CHAR(v.date_vente, 'HH24:MI') as heure,
                    v.total_vente,
                    u.nom as vendeur
                FROM vente v
                JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
                WHERE DATE(v.date_vente) = CURRENT_DATE
            """
            params_recent = []
            
            if not is_admin:
                query_recent += " AND v.id_utilisateur = %s"
                params_recent.append(user_id)
            
            query_recent += " ORDER BY v.date_vente DESC LIMIT 5"
            
            cur.execute(query_recent, tuple(params_recent))
            recent_sales = cur.fetchall()

            for sale in recent_sales:
                self.recent_sales_tree.insert(
                    '',
                    tk.END,
                    values=(
                        f"#{sale['id_vente']}",
                        sale['vendeur'],
                        sale['heure'],
                        f"{sale['total_vente']:.2f}"
                    )
                )

            if not recent_sales:
                self.recent_sales_tree.insert('', tk.END, values=("Aucune", "-", "-", "-"))
            cur.close()
            conn.close()

        except Exception as e:
            print(f"Erreur lors du chargement des graphiques: {e}")

    def update_kpi(self, key, value):
        """Met à jour la valeur d'un KPI"""
        if key in self.kpi_values:
            self.kpi_values[key].config(text=value)

    # ===================== NAVIGATION RAPIDE =====================
    def _navigate(self, FrameClass):
        """Méthode utilitaire pour naviguer via le master principal"""
        try:
            # self.master est 'content' frame
            # self.master.master est BaseFrame, qui a la méthode show_page
            if hasattr(self.master.master, 'show_page'):
                self.master.master.show_page(FrameClass)
            else:
                print("Erreur Nav: method show_page not found on master.master")
        except Exception as e:
            print(f"Erreur lors de la navigation: {e}")

    def go_to_ventes(self):
        try:
            from ui.ventes import VentesFrame
            self._navigate(VentesFrame)
        except ImportError: pass

    def go_to_produits(self):
        try:
            from ui.produits import ProduitsFrame
            self._navigate(ProduitsFrame)
        except ImportError: pass

    def go_to_rapports(self):
        try:
            from ui.rapports import RapportsFrame
            self._navigate(RapportsFrame)
        except ImportError: pass

    def go_to_fournisseurs(self):
        try:
            from ui.fournisseurs import FournisseurFrame
            self._navigate(FournisseurFrame)
        except ImportError: pass

    def go_to_commandes(self):
        try:
            from ui.commandes import CommandeAchatFrame
            self._navigate(CommandeAchatFrame)
        except ImportError: pass

    def go_to_categories(self):
        try:
            from ui.categories import CategorieFrame
            self._navigate(CategorieFrame)
        except ImportError: pass

    def go_to_stock(self):
        try:
            from ui.stock import StockFrame
            self._navigate(StockFrame)
        except ImportError: pass

    def go_to_recus(self):
        try:
            from ui.reçus import ReçusFrame
            self._navigate(ReçusFrame)
        except ImportError: pass