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
            columns=('ID', 'Heure', 'Montant'),
            show='headings',
            height=8
        )
        self.recent_sales_tree.place(x=10, y=50, width=480, height=200)

        # Configuration des colonnes
        self.recent_sales_tree.heading('ID', text='N° Vente')
        self.recent_sales_tree.heading('Heure', text='Heure')
        self.recent_sales_tree.heading('Montant', text='Montant')
        self.recent_sales_tree.column('ID', width=100, anchor='center')
        self.recent_sales_tree.column('Heure', width=150, anchor='center')
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

        # Bouton Ajouter un produit
        tk.Button(
            frame,
            text="Ajouter un produit",
            bg='#0d6efd',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2',
            command=self.go_to_produits
        ).place(x=120, y=15)

        # Bouton Passer une vente
        tk.Button(
            frame,
            text="Passer une vente",
            bg='#198754',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2',
            command=self.go_to_ventes
        ).place(x=360, y=15)

        # Bouton Voir rapports
        tk.Button(
            frame,
            text="Voir rapports",
            bg='#343a40',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2',
            command=self.go_to_rapports
        ).place(x=600, y=15)

    # ===================== CHARGEMENT DES DONNÉES =====================
    def load_dashboard_data(self):
        """Charge les données du dashboard depuis la base"""
        try:
            conn = get_connection()
            if conn is None:
                print("Erreur: Impossible de se connecter à la base de données")
                return

            cur = get_cursor(conn)

            # 1. Chiffre d'affaires du jour
            cur.execute("""
                SELECT COALESCE(SUM(total_vente), 0) as ca_jour
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
            """)
            ca_result = cur.fetchone()
            if ca_result:
                self.update_kpi('ca_jour', f"{ca_result['ca_jour']:,.2f} €")

            # 2. Nombre de ventes du jour
            cur.execute("""
                SELECT COUNT(*) as ventes_jour
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
            """)
            ventes_result = cur.fetchone()
            if ventes_result:
                self.update_kpi('ventes_jour', str(ventes_result['ventes_jour']))

            # 3. Produits en seuil bas (stock <= seuil minimum)
            try:
                # Essayer d'abord avec la vue si elle existe
                cur.execute("""
                    SELECT COUNT(*) as alertes
                    FROM vue_etat_stock 
                    WHERE etat IN ('RUPTURE', 'ALERTE')
                """)
            except:
                # Fallback si la vue n'existe pas
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

            # 4. Nombre total de produits actifs
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

            # 1. TOP 5 PRODUITS VENDUS (30 derniers jours)
            self.top_products_tree.delete(*self.top_products_tree.get_children())

            try:
                # Essayer avec la vue si elle existe
                cur.execute("""
                    SELECT nom, quantite_vendue 
                    FROM vue_top_produits 
                    ORDER BY quantite_vendue DESC 
                    LIMIT 5
                """)
            except:
                # Fallback si la vue n'existe pas
                cur.execute("""
                    SELECT 
                        p.nom_produit as nom,
                        COALESCE(SUM(lv.quantite_vendue), 0) as quantite_vendue
                    FROM produit p
                    LEFT JOIN ligne_vente lv ON p.id_produit = lv.id_produit
                    LEFT JOIN vente v ON lv.id_vente = v.id_vente
                    WHERE v.date_vente >= CURRENT_DATE - INTERVAL '30 days'
                    OR v.date_vente IS NULL
                    GROUP BY p.id_produit, p.nom_produit
                    ORDER BY quantite_vendue DESC
                    LIMIT 5
                """)

            top_products = cur.fetchall()

            for i, product in enumerate(top_products, 1):
                # Ajouter un emoji pour les 3 premiers
                prefix = ""
                if i == 1:
                    prefix = "🥇 "
                elif i == 2:
                    prefix = "🥈 "
                elif i == 3:
                    prefix = "🥉 "

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

            cur.execute("""
                SELECT 
                    id_vente,
                    TO_CHAR(date_vente, 'HH24:MI') as heure,
                    total_vente
                FROM vente 
                WHERE DATE(date_vente) = CURRENT_DATE
                ORDER BY date_vente DESC
                LIMIT 5
            """)

            recent_sales = cur.fetchall()

            for sale in recent_sales:
                self.recent_sales_tree.insert(
                    '',
                    tk.END,
                    values=(
                        f"#{sale['id_vente']}",
                        sale['heure'],
                        f"{sale['total_vente']:.2f} €"
                    )
                )

            # Si pas de ventes aujourd'hui, afficher un message
            if not recent_sales:
                self.recent_sales_tree.insert(
                    '',
                    tk.END,
                    values=("Aucune vente", "aujourd'hui", "-")
                )

            cur.close()
            conn.close()

        except Exception as e:
            print(f"Erreur lors du chargement des graphiques: {e}")

    def update_kpi(self, key, value):
        """Met à jour la valeur d'un KPI"""
        if key in self.kpi_values:
            self.kpi_values[key].config(text=value)

    # ===================== NAVIGATION RAPIDE =====================
    def go_to_ventes(self):
        """Naviguer vers la page des ventes"""
        if self.go_dashboard:
            if hasattr(self.master, 'show_page'):
                try:
                    from ui.ventes import VentesFrame
                    self.master.show_page(VentesFrame)
                except ImportError as e:
                    print(f"Impossible d'importer VentesFrame: {e}")

    def go_to_produits(self):
        """Naviguer vers la page des produits"""
        if self.go_dashboard:
            if hasattr(self.master, 'show_page'):
                try:
                    from ui.produits import ProduitsFrame
                    self.master.show_page(ProduitsFrame)
                except ImportError as e:
                    print(f"Impossible d'importer ProduitsFrame: {e}")

    def go_to_rapports(self):
        """Naviguer vers la page des rapports"""
        if self.go_dashboard:
            if hasattr(self.master, 'show_page'):
                try:
                    from ui.rapports import RapportsFrame
                    self.master.show_page(RapportsFrame)
                except ImportError as e:
                    print(f"Impossible d'importer RapportsFrame: {e}")