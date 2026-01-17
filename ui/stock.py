import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from db.models import get_connection, get_cursor
from db.connection import get_connection, get_cursor


class StockFrame(tk.Frame):
    def __init__(self, parent, user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)

        self.go_dashboard = go_dashboard
        self.user = user

        self.create_title()
        self.create_stats_frame()
        self.create_main_content()

        # Charger les données
        self.load_stats()
        self.load_stock_status()
        self.load_stock_history()
        # Rafraîchissement automatique toutes les 30 secondes
        self.refresh_all()
        self.after(30000, self.auto_refresh)  # 30 secondes

    def auto_refresh(self):
        """Rafraîchit automatiquement les données"""
        self.refresh_all()
        self.after(30000, self.auto_refresh)

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

        # Stocker les références aux labels de valeur
        self.stat_labels = {}

        # Carte 1 : Total articles
        self.total_card, label = self.create_stat_card(
            stats_frame,
            "Total articles en stock",
            "0",
            "#0d6efd",
            "📊"
        )
        self.total_card.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        self.stat_labels['total'] = label  # Stocke la référence

        # Carte 2 : Produits en alerte
        self.alert_card, label = self.create_stat_card(
            stats_frame,
            "Produits en alerte",
            "0",
            "#dc3545",
            "⚠️"
        )
        self.alert_card.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        self.stat_labels['alerte'] = label

        # Carte 3 : Dernière mise à jour
        self.update_card, label = self.create_stat_card(
            stats_frame,
            "Dernière mise à jour",
            datetime.now().strftime("%H:%M"),
            "#198754",
            "🕒"
        )
        self.update_card.grid(row=0, column=2, padx=5, pady=5, sticky='nsew')
        self.stat_labels['update'] = label

        # Configurer les colonnes
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)

    def create_stat_card(self, parent, title, value, color, icon):
        """Crée une carte de statistique - retourne (frame, label)"""
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

        return card, value_label  # Retourne le frame ET le label
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
        self.stock_tree.tag_configure('rupture', background='#ffcccc')

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

    # ===================== LOGIQUE - CONNEXION BD =====================
    def load_stats(self):
        """Charge les statistiques depuis la vue SQL"""
        conn = get_connection()
        if not conn:
            messagebox.showerror("Erreur", "Connexion BD impossible")
            return

        cur = get_cursor(conn)
        try:
            # 1. Total articles en stock
            cur.execute("SELECT SUM(quantite_stock) FROM produit")
            total_articles = cur.fetchone()['sum'] or 0

            # 2. Produits en alerte (via vue_etat_stock)
            cur.execute("""
                SELECT COUNT(*) 
                FROM vue_etat_stock 
                WHERE etat IN ('ALERTE', 'RUPTURE')
            """)
            produits_alerte = cur.fetchone()['count'] or 0

            # 3. Dernière mise à jour
            cur.execute("""
                SELECT MAX(date_mouvement) as derniere_maj 
                FROM mouvement_stock
            """)
            derniere_maj = cur.fetchone()['derniere_maj']

            # Mettre à jour l'interface
            self.update_stats_ui(total_articles, produits_alerte, derniere_maj)

        except Exception as e:
            print(f"Erreur load_stats: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les stats: {e}")
        finally:
            cur.close()
            conn.close()

    def update_stats_ui(self, total_articles, produits_alerte, derniere_maj):
        """Met à jour l'affichage des statistiques"""
        # Utiliser les labels stockés dans le dictionnaire
        if 'total' in self.stat_labels:
            self.stat_labels['total'].config(text=f"{total_articles:,}")

        if 'alerte' in self.stat_labels:
            self.stat_labels['alerte'].config(text=str(produits_alerte))

        if 'update' in self.stat_labels:
            if derniere_maj:
                heure = derniere_maj.strftime("%H:%M")
                self.stat_labels['update'].config(text=heure)
            else:
                self.stat_labels['update'].config(text="--:--")
    def load_stock_status(self):
        """Charge l'état du stock depuis la vue SQL"""
        self.stock_tree.delete(*self.stock_tree.get_children())

        conn = get_connection()
        if not conn:
            messagebox.showerror("Erreur", "Connexion BD impossible")
            return

        cur = get_cursor(conn)
        try:
            # Utiliser la vue vue_etat_stock
            cur.execute("""
                SELECT * FROM vue_etat_stock 
                ORDER BY 
                    CASE etat 
                        WHEN 'RUPTURE' THEN 1
                        WHEN 'ALERTE' THEN 2
                        ELSE 3
                    END,
                    quantite_stock ASC
            """)

            produits = cur.fetchall()

            for prod in produits:
                # Déterminer le tag (couleur)
                if prod['etat'] == 'RUPTURE':
                    tag = 'rupture'
                    statut_display = 'RUPTURE'
                elif prod['etat'] == 'ALERTE':
                    tag = 'alerte'
                    statut_display = 'ALERTE'
                else:
                    tag = 'ok'
                    statut_display = 'OK'

                self.stock_tree.insert(
                    '',
                    tk.END,
                    values=(
                        prod['id_produit'],
                        prod['nom'],
                        prod['categorie'],
                        prod['quantite_stock'],
                        prod['seuil_min'],
                        statut_display
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            print(f"Erreur load_stock_status: {e}")
            # Fallback sur les données d'exemple si la vue n'existe pas
            self.load_stock_status_fallback()
        finally:
            cur.close()
            conn.close()

    def load_stock_status_fallback(self):
        """Fallback si la vue n'existe pas encore"""
        produits_exemple = [
            (1, 'Coca-Cola 2L', 'Boissons', 45, 10, 'OK'),
            (2, 'Pain Blanc', 'Boulangerie', 5, 15, 'ALERTE'),
            (3, 'Lait Frais 1L', 'Produits Laitiers', 28, 20, 'OK'),
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
        """Charge l'historique des mouvements depuis la table mouvement_stock"""
        # On ne nettoie QUE l'historique complet ici, l'historique filtré est géré par filter_history
        self.full_history_tree.delete(*self.full_history_tree.get_children())

        conn = get_connection()
        if not conn:
            messagebox.showerror("Erreur", "Connexion BD impossible")
            return

        cur = get_cursor(conn)
        try:
            # Récupérer les mouvements avec jointures
            cur.execute("""
                SELECT 
                    m.date_mouvement,
                    p.nom_produit,
                    m.type_mouvement,
                    m.quantite,
                    u.nom as utilisateur,
                    CASE 
                        WHEN m.id_vente IS NOT NULL THEN 'Vente #' || m.id_vente
                        WHEN m.id_commande_achat IS NOT NULL THEN 'Commande #' || m.id_commande_achat
                        ELSE 'Ajustement'
                    END as origine
                FROM mouvement_stock m
                JOIN produit p ON m.id_produit = p.id_produit
                JOIN utilisateur u ON m.id_utilisateur = u.id_utilisateur
                ORDER BY m.date_mouvement DESC
                LIMIT 50
            """)

            mouvements = cur.fetchall()

            for i, mvt in enumerate(mouvements):
                date_str = mvt['date_mouvement'].strftime("%d/%m %H:%M")
                type_mvt = mvt['type_mouvement']
                quantite = mvt['quantite']

                # Déterminer le tag
                tag = 'entree' if type_mvt.upper() in ['ENTREE', 'AJOUT', 'RECEPTION'] else 'sortie'
                type_display = 'Entrée' if tag == 'entree' else 'Sortie'

                # Historique complet (50 derniers)
                self.full_history_tree.insert(
                    '',
                    tk.END,
                    values=(
                        date_str,
                        mvt['nom_produit'],
                        type_display,
                        quantite,
                        mvt['origine'],
                        mvt['utilisateur']
                    ),
                    tags=(tag,)
                )
            
            # Rafraîchir l'historique filtré (haut droite)
            self.filter_history()

        except Exception as e:
            print(f"Erreur load_stock_history: {e}")
            # Fallback sur les données d'exemple
            self.load_stock_history_fallback()
        finally:
            cur.close()
            conn.close()

    def load_stock_history_fallback(self):
        """Fallback si pas de données"""
        mouvements_exemple = [
            ('13/01 14:30', 'Coca-Cola 2L', 'Entrée', 50, 'Commande #450', 'Jean Dupont'),
            ('13/01 14:25', 'Pain Blanc', 'Sortie', 10, 'Vente #789', 'Marie Curie'),
        ]

        for mouvement in mouvements_exemple:
            date, produit, type_mvt, quantite, origine, utilisateur = mouvement
            tag = 'entree' if type_mvt == 'Entrée' else 'sortie'

            self.history_tree.insert(
                '',
                tk.END,
                values=(date, produit, type_mvt, quantite, origine, utilisateur),
                tags=(tag,)
            )

            self.full_history_tree.insert(
                '',
                tk.END,
                values=(date, produit, type_mvt, quantite, origine, utilisateur),
                tags=(tag,)
            )

    def filter_history(self):
        """Filtre l'historique selon la période sélectionnée"""
        periode = self.period_var.get()

        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)
        try:
            # Déterminer la date de début selon la période
            if periode == '7j':
                date_limit = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                where_clause = f"WHERE m.date_mouvement >= '{date_limit}'"
            elif periode == '30j':
                date_limit = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
                where_clause = f"WHERE m.date_mouvement >= '{date_limit}'"
            else:
                where_clause = ""

            query = f"""
                SELECT 
                    m.date_mouvement,
                    p.nom_produit,
                    m.type_mouvement,
                    m.quantite,
                    u.nom as utilisateur,
                    CASE 
                        WHEN m.id_vente IS NOT NULL THEN 'Vente #' || m.id_vente
                        WHEN m.id_commande_achat IS NOT NULL THEN 'Commande #' || m.id_commande_achat
                        ELSE 'Ajustement'
                    END as origine
                FROM mouvement_stock m
                JOIN produit p ON m.id_produit = p.id_produit
                JOIN utilisateur u ON m.id_utilisateur = u.id_utilisateur
                {where_clause}
                ORDER BY m.date_mouvement DESC
                LIMIT 20
            """

            cur.execute(query)
            mouvements = cur.fetchall()

            # Mettre à jour le treeview
            self.history_tree.delete(*self.history_tree.get_children())

            for mvt in mouvements:
                date_str = mvt['date_mouvement'].strftime("%d/%m %H:%M")
                type_mvt = mvt['type_mouvement']
                tag = 'entree' if type_mvt.upper() in ['ENTREE', 'AJOUT', 'RECEPTION'] else 'sortie'
                type_display = 'Entrée' if tag == 'entree' else 'Sortie'

                self.history_tree.insert(
                    '',
                    tk.END,
                    values=(
                        date_str,
                        mvt['nom_produit'],
                        type_display,
                        mvt['quantite'],
                        mvt['origine'],
                        mvt['utilisateur']
                    ),
                    tags=(tag,)
                )

        except Exception as e:
            print(f"Erreur filter_history: {e}")
        finally:
            cur.close()
            conn.close()

    def refresh_all(self):
        """Rafraîchit toutes les données"""
        self.load_stats()
        self.load_stock_status()
        self.load_stock_history()