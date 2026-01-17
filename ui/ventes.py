import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db.models import get_products_for_sale, process_sale
from db.models import get_connection, get_cursor

class VentesFrame(tk.Frame):
    def __init__(self, parent,user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)
        self.user = user
        self.panier = []  # Liste pour stocker les articles du panier
        self.selected_product = None  # Produit actuellement sélectionné
        self.go_dashboard = go_dashboard

        self.create_title()
        self.create_left_frame()
        self.create_center_frame()
        self.create_right_frame()
        self.go_dashboard = go_dashboard

        # Charger les produits disponibles
        self.load_products()

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
            text='Gestion des Ventes',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== FRAME GAUCHE - PRODUITS DISPONIBLES =====================
    def create_left_frame(self):
        left_frame = tk.Frame(self, bg='white', bd=2, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 5), pady=10)

        # Titre
        tk.Label(
            left_frame,
            text='📦 Produits disponibles',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 5))

        # Barre de recherche
        search_frame = tk.Frame(left_frame, bg='white')
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        self.search_entry = tk.Entry(
            search_frame,
            font=('times new roman', 10),
            bg='lightyellow',
            width=12
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        tk.Button(
            search_frame,
            text='🔍',
            font=('times new roman', 10, 'bold'),
            bg='#0f4d7d',
            fg='white',
            cursor='hand2',
            width=4,
            command=self.search_product
        ).pack(side=tk.LEFT, padx=(0, 2))

        tk.Button(
            search_frame,
            text='🔄',
            font=('times new roman', 10, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            width=4,
            command=self.load_products
        ).pack(side=tk.LEFT)

        # Treeview des produits
        tree_frame = tk.Frame(left_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.products_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Nom', 'Prix', 'Stock'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=15
        )

        v_scrollbar.config(command=self.products_tree.yview)
        h_scrollbar.config(command=self.products_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.products_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        columns = [
            ('ID', 'ID', 35),
            ('Nom', 'Produit', 110),
            ('Prix', 'Prix €', 50),
            ('Stock', 'Stock', 50)
        ]

        for col, text, width in columns:
            self.products_tree.heading(col, text=text)
            self.products_tree.column(col, width=width, anchor=tk.CENTER)

        # Bind la sélection
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)

    # ===================== FRAME CENTRE =====================
    def create_center_frame(self):
        center_frame = tk.Frame(self, bg='#f5f6f8')
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)

        # ===== PANIER (HAUT) =====
        panier_frame = tk.Frame(center_frame, bg='white', bd=2, relief=tk.RIDGE)
        panier_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        tk.Label(
            panier_frame,
            text='🛒 Panier',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 5))

        # Treeview du panier
        panier_tree_frame = tk.Frame(panier_frame, bg='white')
        panier_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbars pour le panier
        panier_v_scroll = tk.Scrollbar(panier_tree_frame, orient=tk.VERTICAL)
        panier_h_scroll = tk.Scrollbar(panier_tree_frame, orient=tk.HORIZONTAL)

        self.panier_tree = ttk.Treeview(
            panier_tree_frame,
            columns=('ID', 'Produit', 'Qté', 'PU', 'Total', 'Action'),
            show='headings',
            yscrollcommand=panier_v_scroll.set,
            xscrollcommand=panier_h_scroll.set,
            height=8
        )

        panier_v_scroll.config(command=self.panier_tree.yview)
        panier_h_scroll.config(command=self.panier_tree.xview)

        panier_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        panier_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.panier_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes du panier
        panier_columns = [
            ('ID', 'ID', 30),
            ('Produit', 'Produit', 85),
            ('Qté', 'Qté', 35),
            ('PU', 'P.U.', 45),
            ('Total', 'Total', 50),
            ('Action', '❌', 35)
        ]

        for col, text, width in panier_columns:
            self.panier_tree.heading(col, text=text)
            self.panier_tree.column(col, width=width, anchor=tk.CENTER)

        # Message si panier vide
        self.panier_empty_label = tk.Label(
            panier_frame,
            text='Le panier est vide\n\nCliquez sur un produit\ngauche puis "Ajouter"',
            font=('times new roman', 10),
            fg='#6c757d',
            bg='white',
            justify=tk.CENTER
        )
        self.panier_empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Bind pour supprimer du panier
        self.panier_tree.bind('<Button-1>', self.on_panier_click)

        # ===== PRODUIT SÉLECTIONNÉ (BAS) =====
        selected_frame = tk.Frame(center_frame, bg='white', bd=2, relief=tk.RIDGE)
        selected_frame.pack(fill=tk.BOTH, pady=(5, 0))

        tk.Label(
            selected_frame,
            text='🎯 Produit sélectionné',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 5))

        # Frame pour les informations du produit
        self.selected_info_frame = tk.Frame(selected_frame, bg='white')
        self.selected_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Message par défaut
        self.selected_empty_label = tk.Label(
            self.selected_info_frame,
            text='Sélectionnez un produit\nà gauche pour voir\nses détails ici',
            font=('times new roman', 10),
            fg='#6c757d',
            bg='white',
            justify=tk.CENTER
        )
        self.selected_empty_label.pack(expand=True)

        # Frame pour les infos produit (caché par défaut)
        self.selected_details_frame = tk.Frame(self.selected_info_frame, bg='white')

        # Informations du produit (centrées)
        self.selected_name_label = tk.Label(
            self.selected_details_frame,
            font=('times new roman', 11, 'bold'),
            bg='white',
            fg='#0f4d7d',
            justify=tk.CENTER,
            wraplength=200
        )
        self.selected_name_label.pack(pady=(5, 0))

        info_frame = tk.Frame(self.selected_details_frame, bg='white')
        info_frame.pack(pady=5)

        self.selected_price_label = tk.Label(
            info_frame,
            font=('times new roman', 10),
            bg='white'
        )
        self.selected_price_label.pack()

        self.selected_stock_label = tk.Label(
            info_frame,
            font=('times new roman', 10),
            bg='white'
        )
        self.selected_stock_label.pack()

        # Quantité et boutons
        control_frame = tk.Frame(self.selected_details_frame, bg='white')
        control_frame.pack(pady=10)

        tk.Label(
            control_frame,
            text='Quantité:',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.quantity_spinbox = tk.Spinbox(
            control_frame,
            from_=1,
            to=100,
            font=('times new roman', 10),
            width=8
        )
        self.quantity_spinbox.pack(side=tk.LEFT, padx=(0, 10))

        # Boutons côte à côte
        button_frame = tk.Frame(self.selected_details_frame, bg='white')
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text='➕ Ajouter',
            font=('times new roman', 10, 'bold'),
            bg='#198754',
            fg='white',
            cursor='hand2',
            width=12,
            command=self.add_to_cart
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            button_frame,
            text='🗑 Effacer',
            font=('times new roman', 10, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            width=12,
            command=self.clear_selection
        ).pack(side=tk.LEFT, padx=2)

    # ===================== FRAME DROITE - RÉCAPITULATIF =====================
    def create_right_frame(self):
        right_frame = tk.Frame(self, bg='white', bd=2, relief=tk.RIDGE)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 20), pady=10)

        tk.Label(
            right_frame,
            text='💰 Récapitulatif',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 15))

        # Statistiques
        stats_frame = tk.Frame(right_frame, bg='white')
        stats_frame.pack(fill=tk.X, padx=15, pady=5)

        # Nombre d'articles
        tk.Label(
            stats_frame,
            text="Articles :",
            font=('times new roman', 11),
            bg='white'
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.articles_count_label = tk.Label(
            stats_frame,
            text="0",
            font=('times new roman', 11, 'bold'),
            bg='white',
            fg='#198754'
        )
        self.articles_count_label.grid(row=0, column=1, sticky='e', pady=5, padx=20)

        # Nombre de lignes
        tk.Label(
            stats_frame,
            text="Lignes :",
            font=('times new roman', 11),
            bg='white'
        ).grid(row=1, column=0, sticky='w', pady=5)

        self.lines_count_label = tk.Label(
            stats_frame,
            text="0",
            font=('times new roman', 11, 'bold'),
            bg='white',
            fg='#0d6efd'
        )
        self.lines_count_label.grid(row=1, column=1, sticky='e', pady=5, padx=20)

        # Séparateur
        tk.Frame(right_frame, bg='#dee2e6', height=1).pack(fill=tk.X, padx=15, pady=15)

        # Total
        total_frame = tk.Frame(right_frame, bg='white')
        total_frame.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(
            total_frame,
            text="TOTAL :",
            font=('times new roman', 13, 'bold'),
            bg='white'
        ).pack(side=tk.LEFT)

        self.total_label = tk.Label(
            total_frame,
            text="0.00 €",
            font=('times new roman', 18, 'bold'),
            fg='#dc3545',
            bg='white'
        )
        self.total_label.pack(side=tk.RIGHT)

        # Bouton Valider
        tk.Button(
            right_frame,
            text="✅ VALIDER LA VENTE",
            font=('times new roman', 12, 'bold'),
            bg='#198754',
            fg='white',
            bd=0,
            cursor='hand2',
            padx=20,
            pady=12,
            command=self.validate_sale
        ).pack(pady=30, padx=15, fill=tk.X)

    # ===================== LOGIQUE =====================
    def load_products(self):
        self.products_tree.delete(*self.products_tree.get_children())

        produits = get_products_for_sale()

        for prod in produits:
            self.products_tree.insert(
                '',
                tk.END,
                values=(
                    prod['id_produit'],
                    prod['nom_produit'],
                    float(prod['prix_unitaire']),
                    prod['quantite_stock']
                )
            )

    def search_product(self):
        keyword = self.search_entry.get().strip().lower()
        self.products_tree.delete(*self.products_tree.get_children())
        products = get_products_for_sale()

        for prod in products:
            if (keyword in prod['nom_produit'].lower() or
                    keyword in str(prod['id_produit']) or
                    keyword in str(prod['prix_unitaire']).lower()):
                self.products_tree.insert(
                    '',
                    tk.END,
                    values=(
                        prod['id_produit'],
                        prod['nom_produit'],
                        float(prod['prix_unitaire']),
                        prod['quantite_stock']
                    )
                )
    def on_product_select(self, event):
        """Gère la sélection d'un produit"""
        selected = self.products_tree.focus()
        if not selected:
            return

        values = self.products_tree.item(selected, 'values')
        if not values:
            return

        # Stocker le produit sélectionné
        self.selected_product = {
            'id': int(values[0]),
            'nom': values[1],
            'prix': float(values[2]),
            'stock': int(values[3])
        }

        # Afficher les informations du produit
        self.selected_empty_label.pack_forget()

        # Configurer les labels
        self.selected_name_label.config(text=self.selected_product['nom'])
        self.selected_price_label.config(text=f"Prix: {self.selected_product['prix']:.2f} €")
        self.selected_stock_label.config(text=f"Stock disponible: {self.selected_product['stock']}")

        # Réinitialiser la spinbox
        self.quantity_spinbox.delete(0, tk.END)
        self.quantity_spinbox.insert(0, "1")

        # Afficher le frame des détails
        self.selected_details_frame.pack(fill=tk.BOTH, expand=True)

    def clear_selection(self):
        """Efface la sélection du produit et le retire du panier si présent"""
        if self.selected_product:
            # Vérifier si le produit est dans le panier et le retirer
            product_id = self.selected_product['id']
            initial_len = len(self.panier)
            self.panier = [item for item in self.panier if item['id'] != product_id]
            
            # Si le panier a changé, mettre à jour l'affichage
            if len(self.panier) != initial_len:
                self.update_cart_display()
                # messagebox.showinfo("Info", "Produit retiré du panier")

        self.selected_product = None
        self.selected_details_frame.pack_forget()
        self.selected_empty_label.pack(expand=True)

        # Désélectionner dans le treeview
        for item in self.products_tree.selection():
            self.products_tree.selection_remove(item)

    def add_to_cart(self):
        """Ajoute le produit sélectionné au panier"""
        if not self.selected_product:
            messagebox.showwarning("Attention", "Aucun produit sélectionné")
            return

        try:
            quantity = int(self.quantity_spinbox.get())
            if quantity <= 0:
                messagebox.showwarning("Erreur", "La quantité doit être positive")
                return

            if quantity > self.selected_product['stock']:
                messagebox.showwarning("Erreur", "Quantité supérieure au stock disponible")
                return

            # Vérifier si le produit est déjà dans le panier
            for i, item in enumerate(self.panier):
                if item['id'] == self.selected_product['id']:
                    # Augmenter la quantité
                    self.panier[i]['quantité'] += quantity
                    self.panier[i]['sous-total'] = self.panier[i]['quantité'] * self.selected_product['prix']
                    self.update_cart_display()
                    return

            # Ajouter un nouvel article au panier
            new_item = {
                'id': self.selected_product['id'],
                'nom': self.selected_product['nom'],
                'quantité': quantity,
                'prix_unitaire': self.selected_product['prix'],
                'sous-total': quantity * self.selected_product['prix']
            }

            self.panier.append(new_item)
            self.update_cart_display()

        except ValueError:
            messagebox.showwarning("Erreur", "Quantité invalide")

    def update_cart_display(self):
        """Met à jour l'affichage du panier"""
        self.panier_tree.delete(*self.panier_tree.get_children())

        if not self.panier:
            self.panier_empty_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            self.panier_empty_label.place_forget()

            for item in self.panier:
                self.panier_tree.insert(
                    '',
                    tk.END,
                    values=(
                        item['id'],
                        item['nom'],
                        item['quantité'],
                        f"{item['prix_unitaire']:.2f}",
                        f"{item['sous-total']:.2f}",
                        "❌"
                    )
                )

        # Mettre à jour les statistiques
        self.update_stats()

    def on_panier_click(self, event):
        """Gère le clic sur le panier (pour supprimer)"""
        item = self.panier_tree.identify_row(event.y)
        column = self.panier_tree.identify_column(event.x)

        if item and column == '#6':  # Colonne Action
            values = self.panier_tree.item(item, 'values')
            if values:
                product_id = int(values[0])
                product_name = values[1]

                if messagebox.askyesno("Confirmation", f"Supprimer {product_name} du panier ?"):
                    # Retirer du panier
                    self.panier = [item for item in self.panier if item['id'] != product_id]
                    self.update_cart_display()

    def update_stats(self):
        """Met à jour les statistiques du récapitulatif"""
        total_articles = sum(item['quantité'] for item in self.panier)
        total_lines = len(self.panier)
        total_amount = sum(item['sous-total'] for item in self.panier)

        self.articles_count_label.config(text=str(total_articles))
        self.lines_count_label.config(text=str(total_lines))
        self.total_label.config(text=f"{total_amount:.2f} €")

    def validate_sale(self):
        if not self.panier:
            messagebox.showwarning("Attention", "Le panier est vide")
            return

        success, result = process_sale(
            panier=self.panier,
            id_utilisateur=self.user['id_utilisateur']
        )

        if success:
            # Générer et afficher le reçu immédiatement
            receipt_text = self.generate_receipt_text(result)

            # Afficher dans une fenêtre popup
            self.show_receipt_popup(receipt_text, result)

            self.panier = []
            self.update_cart_display()
            self.clear_selection()
            self.load_products()
        else:
            messagebox.showerror("Erreur", result)

    def generate_receipt_text(self, sale_id):
        """Génère le texte du reçu"""
        conn = get_connection()
        cur = get_cursor(conn)

        # Récupérer les infos de la vente
        cur.execute("""
            SELECT v.*, u.nom as vendeur
            FROM vente v
            JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
            WHERE v.id_vente = %s
        """, (sale_id,))

        sale_info = cur.fetchone()

        cur.execute("""
            SELECT p.nom_produit, lv.quantite_vendue, lv.prix_unitaire
            FROM ligne_vente lv
            JOIN produit p ON lv.id_produit = p.id_produit
            WHERE lv.id_vente = %s
        """, (sale_id,))

        items = cur.fetchall()

        # Construire le reçu
        lines = []
        lines.append("=" * 40)
        lines.append("         REÇU DE VENTE")
        lines.append("=" * 40)
        lines.append(f"Vente N° : {sale_id}")
        lines.append(f"Date     : {sale_info['date_vente'].strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Vendeur  : {sale_info['vendeur']}")
        lines.append("-" * 40)
        lines.append(f"{'Produit':<20} {'Qté':>5} {'PU':>8} {'Total':>10}")
        lines.append("-" * 40)

        total = 0
        for item in items:
            nom = item['nom_produit'][:19]
            qte = item['quantite_vendue']
            pu = item['prix_unitaire']
            ligne_total = qte * pu
            total += ligne_total

            lines.append(f"{nom:<20} {qte:>5} {pu:>8.2f} {ligne_total:>10.2f}")

        lines.append("-" * 40)
        lines.append(f"{'TOTAL À PAYER :':<33} {total:>10.2f} €")
        lines.append("=" * 40)
        lines.append("Merci pour votre confiance !")
        lines.append("=" * 40)

        cur.close()
        conn.close()

        return "\n".join(lines)

    def show_receipt_popup(self, receipt_text, sale_id):
        """Affiche le reçu dans une popup"""
        popup = tk.Toplevel()
        popup.title(f"Reçu Vente #{sale_id}")
        popup.geometry("500x600")

        # Text widget pour afficher
        text_widget = tk.Text(popup, font=('Courier', 10), width=60, height=30)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, receipt_text)
        text_widget.config(state='disabled')

        # Boutons
        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="📄 Sauvegarder TXT",
            command=lambda: self.save_receipt_txt(receipt_text, sale_id)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Fermer",
            command=popup.destroy
        ).pack(side=tk.LEFT, padx=5)

    def save_receipt_txt(self, receipt_text, sale_id):
        """Sauvegarde le reçu en TXT"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt")],
            initialfile=f"recu_vente_{sale_id}.txt"
        )

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            messagebox.showinfo("Succès", f"Reçu sauvegardé sous:\n{file_path}")
