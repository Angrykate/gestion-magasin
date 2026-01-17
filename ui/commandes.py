import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db.models import get_connection, get_cursor
from db.connection import get_connection, get_cursor


class CommandeAchatFrame(tk.Frame):
    def __init__(self, parent, user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)

        self.user = user
        self.go_dashboard = go_dashboard
        self.current_mode = "list"  # "list", "new", "detail"
        self.current_commande_id = None
        self.current_commande_id = None
        self.lignes_commande = []  # Pour nouvelle commande
        self.all_commandes_data = []  # Pour le filtrage local

        self.create_title()
        self.create_list_view()  # Vue par défaut

        # Charger les données initiales
        # self.load_suppliers()
        # self.load_products()
        self.load_commandes()

    # ===================== TITRE =====================
    def create_title(self):
        self.title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        self.title_bar.pack(fill=tk.X)

        if self.go_dashboard:
            tk.Button(
                self.title_bar,
                text="⬅ Dashboard",
                font=('times new roman', 11, 'bold'),
                bg='#ffffff',
                fg='#0f4d7d',
                cursor='hand2',
                command=self.go_dashboard
            ).pack(side=tk.LEFT, padx=10)

        self.title_label = tk.Label(
            self.title_bar,
            text='📋 Gestion des Commandes',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        )
        self.title_label.pack(expand=True)

        # Bouton Nouvelle Commande (visible seulement en mode liste)
        self.new_button = tk.Button(
            self.title_bar,
            text="➕ Nouvelle commande",
            font=('times new roman', 11, 'bold'),
            bg='#198754',
            fg='white',
            cursor='hand2',
            command=self.show_new_commande
        )
        self.new_button.pack(side=tk.RIGHT, padx=10)

    # ===================== VUE LISTE DES COMMANDES =====================
    def create_list_view(self):
        """Crée l'interface de liste des commandes"""
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()

        self.current_mode = "list"
        self.title_label.config(text='📋 Gestion des Commandes')
        self.new_button.config(state='normal')

        self.content_frame = tk.Frame(self, bg='#f5f6f8')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Filtres
        filter_frame = tk.Frame(self.content_frame, bg='white', bd=1, relief=tk.RIDGE)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            filter_frame,
            text='Filtres :',
            font=('times new roman', 11, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10, pady=5)

        # Filtre par statut
        tk.Label(
            filter_frame,
            text='Statut :',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.status_filter = ttk.Combobox(
            filter_frame,
            values=['TOUS', 'EN_COURS', 'RECUE', 'ANNULEE'],
            font=('times new roman', 10),
            width=12,
            state='readonly'
        )
        self.status_filter.pack(side=tk.LEFT, padx=5)
        self.status_filter.set('TOUS')
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_commandes)

        # Filtre par fournisseur
        tk.Label(
            filter_frame,
            text='Fournisseur :',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.supplier_filter = ttk.Combobox(
            filter_frame,
            font=('times new roman', 10),
            width=20,
            state='readonly'
        )
        self.supplier_filter.pack(side=tk.LEFT, padx=5)
        self.supplier_filter.set('TOUS')
        self.supplier_filter.bind('<<ComboboxSelected>>', self.filter_commandes)

        # Bouton rafraîchir
        tk.Button(
            filter_frame,
            text='🔄',
            font=('times new roman', 10, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.load_commandes
        ).pack(side=tk.RIGHT, padx=10, pady=5)

        # Tableau des commandes
        table_frame = tk.Frame(self.content_frame, bg='white', bd=2, relief=tk.RIDGE)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.commandes_tree = ttk.Treeview(
            table_frame,
            columns=('ID', 'Fournisseur', 'Date', 'Statut', 'Montant', 'Utilisateur'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=18
        )

        v_scrollbar.config(command=self.commandes_tree.yview)
        h_scrollbar.config(command=self.commandes_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.commandes_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        columns = [
            ('ID', 'N°', 50),
            ('Fournisseur', 'Fournisseur', 150),
            ('Date', 'Date', 100),
            ('Statut', 'Statut', 100),
            ('Montant', 'Montant', 100),
            ('Utilisateur', 'Créée par', 120),
        ]

        for col, text, width in columns:
            self.commandes_tree.heading(col, text=text)
            self.commandes_tree.column(col, width=width, anchor=tk.CENTER)

        # Tags pour les couleurs de statut
        self.commandes_tree.tag_configure('en_cours', background='#fff3cd')
        self.commandes_tree.tag_configure('recue', background='#d4edda')
        self.commandes_tree.tag_configure('annulee', background='#f8d7da')

        # Bind la sélection
        self.load_suppliers()  # Pour charger les filtres
        self.load_commandes()  # Pour charger la liste

        # Double-clic pour voir détail
        self.commandes_tree.bind('<Double-Button-1>', self.on_tree_double_click)

        # Menu contextuel (clic droit)
        self.context_menu = tk.Menu(self, tearoff=0, font=('times new roman', 10))
        self.context_menu.add_command(label="👁️ Voir les détails", command=self.show_selected_detail)
        self.context_menu.add_command(label="📦 Réceptionner", command=self.receptionner_selected)
        self.context_menu.add_command(label="❌ Annuler", command=self.annuler_selected)

        # Bind clic droit
        self.commandes_tree.bind('<Button-3>', self.show_context_menu)

    # ===================== VUE NOUVELLE COMMANDE =====================
    def create_new_commande_view(self):
        """Crée l'interface de nouvelle commande"""
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()

        self.current_mode = "new"
        self.title_label.config(text='➕ Nouvelle Commande')
        self.new_button.config(state='disabled')

        self.content_frame = tk.Frame(self, bg='#f5f6f8')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # ===== SECTION HAUTE : INFOS GÉNÉRALES =====
        info_frame = tk.LabelFrame(
            self.content_frame,
            text=' Informations générales ',
            font=('times new roman', 12, 'bold'),
            bg='white',
            fg='#0f4d7d'
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Fournisseur
        tk.Label(
            info_frame,
            text='Fournisseur :',
            font=('times new roman', 11, 'bold'),
            bg='white'
        ).grid(row=0, column=0, padx=20, pady=10, sticky='w')

        self.supplier_combobox = ttk.Combobox(
            info_frame,
            font=('times new roman', 11),
            width=30,
            state='readonly'
        )
        self.supplier_combobox.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        # Date (auto)
        tk.Label(
            info_frame,
            text='Date :',
            font=('times new roman', 11, 'bold'),
            bg='white'
        ).grid(row=0, column=2, padx=20, pady=10, sticky='w')

        current_date = datetime.now().strftime("%d/%m/%Y")
        tk.Label(
            info_frame,
            text=current_date,
            font=('times new roman', 11),
            bg='white',
            fg='#6c757d'
        ).grid(row=0, column=3, padx=10, pady=10, sticky='w')

        # Statut (auto)
        tk.Label(
            info_frame,
            text='Statut :',
            font=('times new roman', 11, 'bold'),
            bg='white'
        ).grid(row=0, column=4, padx=20, pady=10, sticky='w')

        tk.Label(
            info_frame,
            text='EN_COURS',
            font=('times new roman', 11, 'bold'),
            bg='white',
            fg='#dc3545'
        ).grid(row=0, column=5, padx=10, pady=10, sticky='w')

        # ===== SECTION MILIEU : AJOUT DE PRODUITS =====
        products_frame = tk.LabelFrame(
            self.content_frame,
            text=' Produits à commander ',
            font=('times new roman', 12, 'bold'),
            bg='white',
            fg='#0f4d7d'
        )
        products_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Contrôles d'ajout
        add_frame = tk.Frame(products_frame, bg='white')
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            add_frame,
            text='Produit :',
            font=('times new roman', 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.product_combobox = ttk.Combobox(
            add_frame,
            font=('times new roman', 11),
            width=25,
            state='readonly'
        )
        self.product_combobox.pack(side=tk.LEFT, padx=5)
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_change)

        tk.Label(
            add_frame,
            text='Quantité :',
            font=('times new roman', 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.quantity_spinbox = tk.Spinbox(
            add_frame,
            from_=1,
            to=1000,
            font=('times new roman', 11),
            width=8
        )
        self.quantity_spinbox.pack(side=tk.LEFT, padx=5)

        tk.Label(
            add_frame,
            text='Prix unitaire :',
            font=('times new roman', 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(20, 5))

        self.price_entry = tk.Entry(
            add_frame,
            font=('times new roman', 11),
            width=10,
            state='readonly'
        )
        self.price_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(
            add_frame,
            text='€',
            font=('times new roman', 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 20))

        # Bouton Ajouter
        tk.Button(
            add_frame,
            text='➕ Ajouter au panier',
            font=('times new roman', 11, 'bold'),
            bg='#0d6efd',
            fg='white',
            cursor='hand2',
            command=self.add_ligne_commande
        ).pack(side=tk.LEFT)

        # Tableau des lignes de commande
        table_frame = tk.Frame(products_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.lignes_tree = ttk.Treeview(
            table_frame,
            columns=('ID', 'Produit', 'Quantité', 'Prix unitaire', 'Total', 'Action'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=8
        )

        v_scrollbar.config(command=self.lignes_tree.yview)
        h_scrollbar.config(command=self.lignes_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.lignes_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        ligne_columns = [
            ('ID', 'ID', 40),
            ('Produit', 'Produit', 150),
            ('Quantité', 'Qté', 60),
            ('Prix unitaire', 'P.U.', 80),
            ('Total', 'Total', 80),
            ('Action', '❌', 40)
        ]

        for col, text, width in ligne_columns:
            self.lignes_tree.heading(col, text=text)
            self.lignes_tree.column(col, width=width, anchor=tk.CENTER)

        # Message si panier vide
        self.empty_cart_label = tk.Label(
            products_frame,
            text='Aucun produit dans le panier\n\nAjoutez des produits ci-dessus',
            font=('times new roman', 11),
            fg='#6c757d',
            bg='white',
            justify=tk.CENTER
        )
        self.empty_cart_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        # Bind pour supprimer
        self.lignes_tree.bind('<Button-1>', self.on_ligne_click)

        # ===== SECTION BAS : TOTAL ET BOUTONS =====
        bottom_frame = tk.Frame(self.content_frame, bg='#f5f6f8')
        bottom_frame.pack(fill=tk.X, pady=(0, 10))

        # Total
        total_frame = tk.Frame(bottom_frame, bg='white', bd=1, relief=tk.SUNKEN)
        total_frame.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(
            total_frame,
            text='TOTAL COMMANDE :',
            font=('times new roman', 12, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT, padx=10, pady=8)

        self.total_label = tk.Label(
            total_frame,
            text='0.00 €',
            font=('times new roman', 14, 'bold'),
            bg='white',
            fg='#dc3545'
        )
        self.total_label.pack(side=tk.LEFT, padx=(0, 10), pady=8)

        # Boutons
        button_frame = tk.Frame(bottom_frame, bg='#f5f6f8')
        button_frame.pack(side=tk.RIGHT)

        tk.Button(
            button_frame,
            text='🗑 Annuler',
            font=('times new roman', 12, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            width=15,
            command=self.show_list_view
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text='💾 Enregistrer brouillon',
            font=('times new roman', 12, 'bold'),
            bg='#ffc107',
            fg='black',
            cursor='hand2',
            width=20,
            command=self.save_draft
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text='✅ Valider la commande',
            font=('times new roman', 12, 'bold'),
            bg='#198754',
            fg='white',
            cursor='hand2',
            width=20,
            command=self.save_commande
        ).pack(side=tk.LEFT, padx=5)
        self.load_suppliers_for_new()
        self.load_products_for_new()
        self.update_cart_display()

    def on_product_change(self, event=None):
        nom_produit = self.product_combobox.get()
        if nom_produit in self.product_map:
            details = self.product_map[nom_produit]
            prix = details['prix']
            
            self.price_entry.config(state='normal')
            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, str(prix))
            self.price_entry.config(state='readonly')


    # ===================== VUE DÉTAIL/RÉCEPTION =====================
    def create_detail_view(self, commande_id):
        """Crée l'interface de détail/réception d'une commande"""
        if hasattr(self, 'content_frame'):
            self.content_frame.destroy()

        self.current_mode = "detail"
        self.current_commande_id = commande_id
        self.title_label.config(text=f'📦 Commande #{commande_id}')
        self.new_button.config(state='disabled')

        self.content_frame = tk.Frame(self, bg='#f5f6f8')
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Charger les données de la commande
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            # Infos commande
            cur.execute("""
                SELECT 
                    c.*,
                    f.nom_fournisseur,
                    u.nom as createur
                FROM commande_achat c
                JOIN fournisseur f ON c.id_fournisseur = f.id_fournisseur
                JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
                WHERE c.id_commande_achat = %s
            """, (commande_id,))

            commande_info = cur.fetchone()

            if not commande_info:
                messagebox.showerror("Erreur", "Commande introuvable")
                self.show_list_view()
                return

            # Lignes de commande
            cur.execute("""
                SELECT 
                    lc.*,
                    p.nom_produit
                FROM ligne_commande_achat lc
                JOIN produit p ON lc.id_produit = p.id_produit
                WHERE lc.id_commande_achat = %s
            """, (commande_id,))

            lignes = cur.fetchall()

        except Exception as e:
            print(f"Erreur chargement détail: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger: {e}")
            self.show_list_view()
            return
        finally:
            cur.close()
            conn.close()

        # ===== SECTION HAUTE : INFOS COMMANDE =====
        info_frame = tk.LabelFrame(
            self.content_frame,
            text=' Détails de la commande ',
            font=('times new roman', 12, 'bold'),
            bg='white',
            fg='#0f4d7d'
        )
        info_frame.pack(fill=tk.X, pady=(0, 15))

        # Grille d'informations
        infos = [
            ('N° Commande :', commande_id),
            ('Fournisseur :', commande_info['nom_fournisseur']),
            ('Date :', commande_info['date_commande'].strftime("%d/%m/%Y")),
            ('Statut :', commande_info['statut']),
            ('Créée par :', commande_info['createur']),
            ('Montant total :', f"{self.calculate_total(lignes):.2f} €")
        ]

        for i, (label, value) in enumerate(infos):
            row = i // 3
            col = (i % 3) * 2

            tk.Label(
                info_frame,
                text=label,
                font=('times new roman', 11, 'bold'),
                bg='white'
            ).grid(row=row, column=col, padx=20, pady=10, sticky='w')

            color = '#dc3545' if label == 'Statut :' and value == 'EN_COURS' else '#6c757d'
            tk.Label(
                info_frame,
                text=str(value),
                font=('times new roman', 11),
                bg='white',
                fg=color
            ).grid(row=row, column=col + 1, padx=10, pady=10, sticky='w')

        # ===== SECTION MILIEU : PRODUITS COMMANDÉS =====
        products_frame = tk.LabelFrame(
            self.content_frame,
            text=' Produits commandés ',
            font=('times new roman', 12, 'bold'),
            bg='white',
            fg='#0f4d7d'
        )
        products_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Tableau des produits
        table_frame = tk.Frame(products_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.detail_tree = ttk.Treeview(
            table_frame,
            columns=('ID', 'Produit', 'Quantité', 'Prix unitaire', 'Total'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=8
        )

        v_scrollbar.config(command=self.detail_tree.yview)
        h_scrollbar.config(command=self.detail_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.detail_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        detail_columns = [
            ('ID', 'ID', 40),
            ('Produit', 'Produit', 200),
            ('Quantité', 'Qté', 70),
            ('Prix unitaire', 'P.U.', 90),
            ('Total', 'Total', 90)
        ]

        for col, text, width in detail_columns:
            self.detail_tree.heading(col, text=text)
            self.detail_tree.column(col, width=width, anchor=tk.CENTER)

        # Remplir le tableau
        for ligne in lignes:
            total = ligne['quantite_commandee'] * ligne['prix_unitaire']
            self.detail_tree.insert(
                '',
                tk.END,
                values=(
                    ligne['id_produit'],
                    ligne['nom_produit'],
                    ligne['quantite_commandee'],
                    f"{ligne['prix_unitaire']:.2f}",
                    f"{total:.2f}"
                )
            )

        # ===== SECTION BAS : ACTIONS =====
        action_frame = tk.Frame(self.content_frame, bg='#f5f6f8')
        action_frame.pack(fill=tk.X, pady=(0, 10))

        # Bouton Retour
        tk.Button(
            action_frame,
            text='⬅ Retour à la liste',
            font=('times new roman', 11, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            command=self.show_list_view
        ).pack(side=tk.LEFT, padx=5)

        if commande_info and 'statut' in commande_info:
            # Boutons selon statut
            if commande_info['statut'] == 'EN_COURS':
                # Bouton Réceptionner
                tk.Button(
                    action_frame,
                    text='📦 RÉCEPTIONNER LA COMMANDE',
                    font=('times new roman', 12, 'bold'),
                    bg='#198754',
                    fg='white',
                    cursor='hand2',
                    command=lambda: self.receptionner_commande(commande_id)
                ).pack(side=tk.RIGHT, padx=5)

                # Bouton Annuler
                tk.Button(
                    action_frame,
                    text='❌ Annuler la commande',
                    font=('times new roman', 11, 'bold'),
                    bg='#dc3545',
                    fg='white',
                    cursor='hand2',
                    command=lambda: self.annuler_commande(commande_id)
                ).pack(side=tk.RIGHT, padx=5)

            elif commande_info['statut'] == 'RECUE':
                tk.Label(
                    action_frame,
                    text='✅ COMMANDE DÉJÀ RÉCEPTIONNÉE',
                    font=('times new roman', 12, 'bold'),
                    bg='#f5f6f8',
                    fg='#198754'
                ).pack(side=tk.RIGHT, padx=5)

            elif commande_info['statut'] == 'ANNULEE':
                tk.Label(
                    action_frame,
                    text='❌ COMMANDE ANNULÉE',
                    font=('times new roman', 12, 'bold'),
                    bg='#f5f6f8',
                    fg='#dc3545'
                ).pack(side=tk.RIGHT, padx=5)

    # ===================== LOGIQUE =====================
    def load_suppliers(self):
        """Charge la liste des fournisseurs POUR LES FILTRES seulement"""
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            cur.execute("SELECT id_fournisseur, nom_fournisseur FROM fournisseur ORDER BY nom_fournisseur")
            suppliers = cur.fetchall()

            if suppliers and hasattr(self, 'supplier_filter'):
                # Pour le filtre de la liste
                supplier_names = ['TOUS'] + [s['nom_fournisseur'] for s in suppliers]
                self.supplier_filter['values'] = supplier_names
                self.supplier_filter.set('TOUS')

        except Exception as e:
            print(f"❌ Erreur load_suppliers: {e}")
        finally:
            cur.close()
            conn.close()

    def load_products(self):
        """Charge la liste des produits"""
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            cur.execute("SELECT id_produit, nom_produit, prix_unitaire FROM produit WHERE statut = 'ACTIF' ORDER BY nom_produit")
            products = cur.fetchall()

            if hasattr(self, 'product_combobox'):
                # Format SIMPLE sans ID
                product_names = [p['nom_produit'] for p in products]
                self.product_combobox['values'] = product_names

                # Mapping nom simple -> id et details
                self.product_map = {}
                for p in products:
                    self.product_map[p['nom_produit']] = {
                        'id': p['id_produit'],
                        'prix': p['prix_unitaire']  # Mettre le prix d'achat si dispo, sinon prix unitaire
                    }

                if products:
                    self.product_combobox.current(0)
                    self.on_product_change() # Remplir le premier prix

        except Exception as e:
            print(f"Erreur load_products: {e}")
        finally:
            cur.close()
            conn.close()

    def load_commandes(self):
        """Charge la liste des commandes"""
        self.commandes_tree.delete(*self.commandes_tree.get_children())

        conn = get_connection()
        cur = get_cursor(conn)

        try:
            query = """
                SELECT 
                    c.id_commande_achat,
                    f.nom_fournisseur,
                    c.date_commande,
                    c.statut,
                    u.nom as createur,
                    COALESCE(SUM(lc.quantite_commandee * lc.prix_unitaire), 0) as montant
                FROM commande_achat c
                JOIN fournisseur f ON c.id_fournisseur = f.id_fournisseur
                JOIN utilisateur u ON c.id_utilisateur = u.id_utilisateur
                LEFT JOIN ligne_commande_achat lc ON c.id_commande_achat = lc.id_commande_achat
                GROUP BY c.id_commande_achat, f.nom_fournisseur, c.date_commande, c.statut, u.nom
                ORDER BY c.date_commande DESC
            """

            cur.execute(query)
            commandes = cur.fetchall()

            self.all_commandes_data = []  # Réinitialiser la liste locale

            for cmd in commandes:
                date_str = cmd['date_commande'].strftime("%d/%m/%Y")
                montant = f"{cmd['montant']:.2f} €"

                # Déterminer le tag (couleur) seulement
                if cmd['statut'] == 'EN_COURS':
                    tag = 'en_cours'
                elif cmd['statut'] == 'RECUE':
                    tag = 'recue'
                else:  # ANNULEE
                    tag = 'annulee'

                # Sauvegarder les données pour le filtre
                command_data = {
                    'values': (
                        cmd['id_commande_achat'],
                        cmd['nom_fournisseur'],
                        date_str,
                        cmd['statut'],
                        montant,
                        cmd['createur']
                    ),
                    'tags': (tag,)
                }
                self.all_commandes_data.append(command_data)

                self.commandes_tree.insert(
                    '',
                    tk.END,
                    values=command_data['values'],
                    tags=command_data['tags']
                )

            # Réappliquer le filtre actuel si nécessaire
            if hasattr(self, 'status_filter') and (self.status_filter.get() != 'TOUS' or self.supplier_filter.get() != 'TOUS'):
                self.filter_commandes()

        except Exception as e:
            print(f"Erreur load_commandes: {e}")
        finally:
            cur.close()
            conn.close()

    def on_tree_double_click(self, event):
        """Ouvre le détail d'une commande au double-clic"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values and len(values) > 0:
                try:
                    commande_id = int(values[0])
                    self.show_detail_view(commande_id)
                except (ValueError, IndexError) as e:
                    print(f"Erreur ouverture détail: {e}")

    def show_context_menu(self, event):
        """Affiche le menu contextuel au clic droit"""
        item = self.commandes_tree.identify_row(event.y)
        if item:
            self.commandes_tree.selection_set(item)
            # Afficher le menu à la position de la souris
            self.context_menu.post(event.x_root, event.y_root)

    def show_selected_detail(self):
        """Affiche le détail de la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values and len(values) > 0:
                try:
                    commande_id = int(values[0])
                    self.show_detail_view(commande_id)
                except (ValueError, IndexError) as e:
                    print(f"Erreur show_selected_detail: {e}")

    def receptionner_selected(self):
        """Réceptionne la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values and len(values) >= 4:
                try:
                    commande_id = int(values[0])
                    statut = values[3]

                    if statut == 'EN_COURS':
                        # Appeler la méthode modifiée
                        self.receptionner_commande(commande_id)
                    else:
                        messagebox.showwarning("Attention",
                                               f"Impossible de réceptionner : commande déjà {statut.lower()}")
                except (ValueError, IndexError) as e:
                    print(f"Erreur receptionner_selected: {e}")

    def annuler_selected(self):
        """Annule la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values and len(values) >= 4:
                try:
                    commande_id = int(values[0])
                    statut = values[3]

                    if statut == 'EN_COURS':
                        if messagebox.askyesno("Confirmation",
                                               f"Annuler la commande #{commande_id} ?"):
                            # Appeler la méthode modifiée
                            self.annuler_commande(commande_id)
                    else:
                        messagebox.showwarning("Attention",
                                               f"Impossible d'annuler : commande déjà {statut.lower()}")
                except (ValueError, IndexError) as e:
                    print(f"Erreur annuler_selected: {e}")
    def load_suppliers_for_new(self):
        """Charge les fournisseurs pour la nouvelle commande"""
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            cur.execute("SELECT id_fournisseur, nom_fournisseur FROM fournisseur ORDER BY nom_fournisseur")
            suppliers = cur.fetchall()

            if suppliers:
                # Pour le combobox de nouvelle commande
                supplier_names = [s['nom_fournisseur'] for s in suppliers]
                self.supplier_combobox['values'] = supplier_names
                self.supplier_combobox.current(0)  # Sélectionner le premier

                # Stocker le mapping nom -> id
                self.supplier_map = {s['nom_fournisseur']: s['id_fournisseur'] for s in suppliers}
                print(f"✅ {len(suppliers)} fournisseurs chargés pour nouvelle commande")

        except Exception as e:
            print(f"❌ Erreur load_suppliers_for_new: {e}")
        finally:
            cur.close()
            conn.close()

    def load_products_for_new(self):
        """Charge les produits pour la nouvelle commande"""
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            cur.execute("SELECT id_produit, nom_produit, prix_unitaire FROM produit WHERE statut = 'ACTIF' ORDER BY nom_produit")
            products = cur.fetchall()

            if products:
                # Pour le combobox de nouvelle commande
                product_names = [p['nom_produit'] for p in products]
                self.product_combobox['values'] = product_names
                self.product_combobox.current(0)  # Sélectionner le premier

                # Stocker le mapping nom -> id et details
                self.product_map = {}
                for p in products:
                    self.product_map[p['nom_produit']] = {
                        'id': p['id_produit'],
                        'prix': p['prix_unitaire']
                    }
                print(f"✅ {len(products)} produits chargés pour nouvelle commande")

        except Exception as e:
            print(f"❌ Erreur load_products_for_new: {e}")
        finally:
            cur.close()
            conn.close()
    def filter_commandes(self, event=None):
        """Filtre les commandes selon les critères en utilisant les données en mémoire"""
        status = self.status_filter.get()
        supplier = self.supplier_filter.get()

        # Vider le tableau
        self.commandes_tree.delete(*self.commandes_tree.get_children())

        # Repeupler selon les filtres
        for cmd in self.all_commandes_data:
            values = cmd['values']
            
            # values[3] est le statut, values[1] est le fournisseur
            status_match = (status == 'TOUS') or (values[3] == status)
            supplier_match = (supplier == 'TOUS') or (values[1] == supplier)

            if status_match and supplier_match:
                self.commandes_tree.insert(
                    '',
                    tk.END,
                    values=values,
                    tags=cmd['tags']
                )

    # def on_tree_click(self, event):
    #     """Gère les clics sur le tableau"""
    #     item = self.commandes_tree.identify_row(event.y)
    #     column = self.commandes_tree.identify_column(event.x)
    #
    #     if item and column == '#7':  # Colonne Actions
    #         values = self.commandes_tree.item(item, 'values')
    #         if values:
    #             commande_id = int(values[0])
    #
    #             if "❌" in values[6] and "🔒" not in values[6]:
    #                 # Bouton ❌ pour annuler (seulement si EN_COURS)
    #                 if messagebox.askyesno("Confirmation", f"Annuler la commande #{commande_id} ?"):
    #                     self.annuler_commande(commande_id)
    #             else:
    #                 # Bouton 👁️ pour voir
    #                 self.show_detail_view(commande_id)

    def show_new_commande(self):
        """Affiche l'interface de nouvelle commande"""
        self.lignes_commande = []
        self.create_new_commande_view()
        self.update_cart_display()

    def show_list_view(self):
        """Retourne à la liste des commandes"""
        self.create_list_view()

    def show_detail_view(self, commande_id):
        """Affiche le détail d'une commande"""
        self.create_detail_view(commande_id)

    def add_ligne_commande(self):
        """Ajoute une ligne au panier de commande"""
        product_name = self.product_combobox.get()  # Juste le nom maintenant
        quantity = self.quantity_spinbox.get()
        price = self.price_entry.get()

        if not product_name or not quantity or not price:
            messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
            return

        try:
            # Utiliser le mapping par nom simple
            product_details = self.product_map.get(product_name)

            if not product_details:
                messagebox.showerror("Erreur", f"Produit '{product_name}' non trouvé")
                return

            product_id = product_details['id']

            quantity = int(quantity)
            price = float(price)

            if quantity <= 0:
                raise ValueError("Quantité positive requise")
            if price <= 0:
                raise ValueError("Prix positif requis")

            # Ajouter au panier
            self.lignes_commande.append({
                'id_produit': product_id,
                'nom': product_name,  # Nom simple
                'quantite': quantity,
                'prix': price,
                'total': quantity * price
            })

            # Mettre à jour l'affichage
            self.update_cart_display()

            # Réinitialiser les champs
            self.quantity_spinbox.delete(0, tk.END)
            self.quantity_spinbox.insert(0, "1")
            self.price_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Erreur", f"Données invalides: {e}")

    def show_selected_detail(self):
        """Affiche le détail de la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values:
                self.show_detail_view(int(values[0]))

    def receptionner_selected(self):
        """Réceptionne la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values:
                self.receptionner_commande(int(values[0]))

    def annuler_selected(self):
        """Annule la commande sélectionnée"""
        selection = self.commandes_tree.selection()
        if selection:
            values = self.commandes_tree.item(selection[0], 'values')
            if values:
                self.annuler_commande(int(values[0]))

    def update_cart_display(self):
        """Met à jour l'affichage du panier"""
        self.lignes_tree.delete(*self.lignes_tree.get_children())

        if not self.lignes_commande:
            self.empty_cart_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
        else:
            self.empty_cart_label.place_forget()

            for ligne in self.lignes_commande:
                self.lignes_tree.insert(
                    '',
                    tk.END,
                    values=(
                        ligne['id_produit'],
                        ligne['nom'],
                        ligne['quantite'],
                        f"{ligne['prix']:.2f}",
                        f"{ligne['total']:.2f}",
                        "❌"
                    )
                )

        # Mettre à jour le total
        total = sum(l['total'] for l in self.lignes_commande)
        self.total_label.config(text=f"{total:.2f} €")

    def on_ligne_click(self, event):
        """Gère le clic sur une ligne du panier"""
        item = self.lignes_tree.identify_row(event.y)
        column = self.lignes_tree.identify_column(event.x)

        if item and column == '#6':  # Colonne Action
            values = self.lignes_tree.item(item, 'values')
            if values:
                product_id = int(values[0])

                # Retirer du panier
                self.lignes_commande = [l for l in self.lignes_commande if l['id_produit'] != product_id]
                self.update_cart_display()

    def save_draft(self):
        """Enregistre comme brouillon (pas implémenté dans cette version)"""
        messagebox.showinfo("Brouillon", "Fonctionnalité brouillon à implémenter")

    def save_commande(self):
        """Enregistre la commande dans la base"""
        supplier_name = self.supplier_combobox.get()

        if not supplier_name:
            messagebox.showwarning("Attention", "Veuillez sélectionner un fournisseur")
            return

        if not self.lignes_commande:
            messagebox.showwarning("Attention", "Le panier est vide")
            return

        # Déclarer les variables AVANT le try
        conn = get_connection()
        cur = get_cursor(conn)

        try:
            supplier_id = self.supplier_map[supplier_name]

            conn = get_connection()
            cur = get_cursor(conn)

            # 1. Créer la commande
            cur.execute("""
                INSERT INTO commande_achat (id_fournisseur, id_utilisateur, statut)
                VALUES (%s, %s, %s)
                RETURNING id_commande_achat
            """, (supplier_id, self.user['id_utilisateur'], 'EN_COURS'))

            commande_id = cur.fetchone()['id_commande_achat']

            # 2. Ajouter les lignes
            for ligne in self.lignes_commande:
                cur.execute("""
                    INSERT INTO ligne_commande_achat 
                    (id_commande_achat, id_produit, quantite_commandee, prix_unitaire)
                    VALUES (%s, %s, %s, %s)
                """, (commande_id, ligne['id_produit'], ligne['quantite'], ligne['prix']))

            conn.commit()

            messagebox.showinfo("Succès", f"Commande #{commande_id} créée avec succès")

            # Retour à la liste
            self.show_list_view()
            self.load_commandes()

        except Exception as e:
            print(f"Erreur save_commande: {e}")
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {e}")
            if conn:
                conn.rollback()
        finally:
            # Vérifier si les variables existent avant de les fermer
            if cur:
                cur.close()
            if conn:
                conn.close()

    def calculate_total(self, lignes):
        """Calcule le total d'une liste de lignes"""
        return sum(l['quantite_commandee'] * l['prix_unitaire'] for l in lignes)

    def receptionner_commande(self, commande_id):
        """Marque une commande comme réceptionnée"""
        if not messagebox.askyesno("Confirmation",
                                   "Réceptionner cette commande ?\n\n"
                                   "Cette action va :\n"
                                   "• Augmenter les stocks\n"
                                   "• Créer des mouvements de stock\n"
                                   "• Verrouiller la commande"):
            return

        conn = None
        cur = None

        try:
            conn = get_connection()
            cur = get_cursor(conn)

            # 1. Vérifier que la commande est EN_COURS
            cur.execute("SELECT statut FROM commande_achat WHERE id_commande_achat = %s", (commande_id,))
            result = cur.fetchone()

            if not result:
                messagebox.showerror("Erreur", "Commande introuvable")
                return

            statut = result['statut']

            if statut != 'EN_COURS':
                messagebox.showerror("Erreur", f"Commande déjà {statut.lower()}")
                return

            # 2. Mettre à jour le statut (le trigger gère le reste)
            cur.execute("""
                UPDATE commande_achat 
                SET statut = 'RECUE'
                WHERE id_commande_achat = %s
            """, (commande_id,))

            conn.commit()

            messagebox.showinfo("Succès", f"Commande #{commande_id} réceptionnée !\n\n"
                                          "• Stock mis à jour\n"
                                          "• Mouvements créés")

            self.show_list_view()
            self.load_commandes()  # Rafraîchir la liste seulement

        except Exception as e:
            print(f"Erreur receptionner_commande: {e}")
            messagebox.showerror("Erreur", f"Impossible de réceptionner: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    def annuler_commande(self, commande_id):
        """Annule une commande"""
        if not messagebox.askyesno("Confirmation",
                                   "Annuler cette commande ?\n\n"
                                   "Cette action est irréversible."):
            return

        conn = None
        cur = None

        try:
            conn = get_connection()
            cur = get_cursor(conn)

            # Vérifier que la commande existe
            cur.execute("SELECT statut FROM commande_achat WHERE id_commande_achat = %s", (commande_id,))
            result = cur.fetchone()

            if not result:
                messagebox.showerror("Erreur", "Commande introuvable")
                return

            statut = result['statut']

            if statut != 'EN_COURS':
                messagebox.showerror("Erreur", f"Impossible d'annuler une commande {statut.lower()}")
                return

            # Mettre à jour le statut
            cur.execute("""
                UPDATE commande_achat 
                SET statut = 'ANNULEE'
                WHERE id_commande_achat = %s
            """, (commande_id,))

            conn.commit()

            messagebox.showinfo("Succès", f"Commande #{commande_id} annulée")

            self.show_list_view()
            self.load_commandes()  # Rafraîchir la liste

        except Exception as e:
            print(f"Erreur annuler_commande: {e}")
            messagebox.showerror("Erreur", f"Impossible d'annuler: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()