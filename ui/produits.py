import tkinter as tk
from tkinter import ttk, messagebox
from db.models import (
    add_product,
    get_all_products,
    update_product,
    delete_product,
    get_product_by_id,
    get_categories_for_dropdown,
)


class ProduitsFrame(tk.Frame):
    def __init__(self, parent,user =None,go_dashboard=None):
        super().__init__(parent, bg='white')
        self.pack(fill=tk.BOTH, expand=True)
        self.is_clearing = False
        self.product_frame = tk.Frame(self, width=1070, height=567, bg='white')
        self.product_frame.pack(fill=tk.BOTH, expand=True)

        self.category_map = {}

        self.create_left_frame()
        self.create_search_frame()
        self.create_treeview()
        self.load_initial_data()

    # ===================== LEFT FRAME - FORMULAIRE =====================
    def create_left_frame(self):
        left_frame = tk.Frame(self.product_frame, bg='white', bd=2, relief=tk.RIDGE)
        left_frame.place(x=20, y=10, width=450, height=547)

        # Titre
        heading_label = tk.Label(
            left_frame,
            text='Manage Product Details',
            font=('times new roman', 16, 'bold'),
            bg='#0f4d7d',
            fg='white'
        )
        heading_label.grid(row=0, columnspan=2, sticky='we', ipady=10)

        # Category
        tk.Label(
            left_frame,
            text='Category',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=1, column=0, padx=20, pady=(20, 10), sticky='w')

        self.category_combobox = ttk.Combobox(
            left_frame,
            font=('times new roman', 12),
            width=22,
            state='readonly'
        )
        self.category_combobox.bind("<<ComboboxSelected>>", self.on_category_change)
        self.category_combobox.grid(row=1, column=1, pady=(20, 10), sticky='w')
        self.category_combobox.set('Select Category')

        # Name
        tk.Label(
            left_frame,
            text='Name',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=2, column=0, padx=20, pady=10, sticky='w')

        self.name_entry = tk.Entry(
            left_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=25
        )
        self.name_entry.grid(row=2, column=1, pady=10, sticky='w')

        # Price
        tk.Label(
            left_frame,
            text='Price',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=3, column=0, padx=20, pady=10, sticky='w')

        self.price_entry = tk.Entry(
            left_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=25
        )
        self.price_entry.grid(row=3, column=1, pady=10, sticky='w')

        # Quantity
        tk.Label(
            left_frame,
            text='Quantity',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=4, column=0, padx=20, pady=10, sticky='w')

        self.quantity_entry = tk.Entry(
            left_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=25
        )
        self.quantity_entry.grid(row=4, column=1, pady=10, sticky='w')

        # Statut
        tk.Label(
            left_frame,
            text='Statut',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=5, column=0, padx=20, pady=10, sticky='w')

        self.statut_combobox = ttk.Combobox(
            left_frame,
            values=('ACTIF', 'INACTIF'),
            font=('times new roman', 12),
            width=20,
            state='readonly'
        )
        self.statut_combobox.grid(row=5, column=1, pady=10, sticky='w')
        self.statut_combobox.set('Select Statut')

        # Seuil min
        tk.Label(
            left_frame,
            text='Seuil min',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=6, column=0, padx=20, pady=10, sticky='w')

        self.seuil_min_entry = tk.Entry(
            left_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=25
        )
        self.seuil_min_entry.grid(row=6, column=1, pady=10, sticky='w')

        # Description
        tk.Label(
            left_frame,
            text='Description',
            font=('times new roman', 14, 'bold'),
            bg='white'
        ).grid(row=7, column=0, padx=20, pady=10, sticky='w')

        self.desc_text = tk.Text(
            left_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=25,
            height=3
        )
        self.desc_text.grid(row=7, column=1, pady=10, sticky='w')

        # Boutons
        button_frame = tk.Frame(left_frame, bg='white')
        button_frame.grid(row=8, columnspan=2, pady=(20, 0))

        buttons = [
            ('Add', '#198754', self.add_product),
            ('Update', '#0d6efd', self.update_product),
            ('Delete', '#dc3545', self.delete_product),
            ('Clear', '#6c757d', self.clear_form)
        ]

        for i, (text, color, cmd) in enumerate(buttons):
            tk.Button(
                button_frame,
                text=text,
                font=('times new roman', 12, 'bold'),
                width=10,
                cursor='hand2',
                bg=color,
                fg='white',
                command=cmd
            ).grid(row=0, column=i, padx=5)

    def on_category_change(self, event=None):
        cat_name = self.category_combobox.get()
        cat = self.category_map.get(cat_name)

        if not cat:
            return

        # Remplir le seuil
        self.seuil_min_entry.delete(0, tk.END)
        self.seuil_min_entry.insert(0, str(cat['seuil']))

    # ===================== SEARCH FRAME =====================
    def create_search_frame(self):
        search_frame = tk.LabelFrame(
            self.product_frame,
            text='Search Product',
            font=('times new roman', 14, 'bold'),
            bg='white'
        )
        search_frame.place(x=480, y=10, width=570, height=70)

        # Critère de recherche
        self.search_combobox = ttk.Combobox(
            search_frame,
            values=('Category', 'Name', 'Price', 'Quantity', 'Statut'),
            font=('times new roman', 12),
            state='readonly',
            width=15
        )
        self.search_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.search_combobox.set('Search By')

        # Champ de recherche
        self.search_entry = tk.Entry(
            search_frame,
            font=('times new roman', 12),
            bg='lightyellow',
            width=20
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=10)

        # Boutons de recherche
        tk.Button(
            search_frame,
            text='Search',
            font=('times new roman', 12, 'bold'),
            width=8,
            cursor='hand2',
            bg='#0f4d7d',
            fg='white',
            command=self.search_product
        ).grid(row=0, column=2, padx=5, pady=10)

        tk.Button(
            search_frame,
            text='Show All',
            font=('times new roman', 12, 'bold'),
            width=8,
            cursor='hand2',
            bg='#6c757d',
            fg='white',
            command=self.load_products
        ).grid(row=0, column=3, padx=5, pady=10)

    # ===================== TREEVIEW =====================
    def create_treeview(self):
        treeview_frame = tk.Frame(self.product_frame, bg='white')
        treeview_frame.place(x=480, y=95, width=570, height=462)

        # Scrollbars
        scrolly = tk.Scrollbar(treeview_frame, orient=tk.VERTICAL)
        scrollx = tk.Scrollbar(treeview_frame, orient=tk.HORIZONTAL)

        # Treeview
        self.treeview = ttk.Treeview(
            treeview_frame,
            columns=('ID', 'Category', 'Nom', 'Prix', 'Quantité', 'Statut', 'Seuil_min', 'Description', 'Date'),
            show='headings',
            yscrollcommand=scrolly.set,
            xscrollcommand=scrollx.set
        )

        # Configuration des scrollbars
        scrolly.pack(side=tk.RIGHT, fill=tk.Y)
        scrollx.pack(side=tk.BOTTOM, fill=tk.X)
        scrolly.config(command=self.treeview.yview)
        scrollx.config(command=self.treeview.xview)
        self.treeview.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        columns = [
            ('ID', 'ID', 50),
            ('Category', 'Category', 100),
            ('Nom', 'Nom', 120),
            ('Prix', 'Prix', 80),
            ('Quantité', 'Quantité', 70),
            ('Statut', 'Statut', 80),
            ('Seuil_min', 'Seuil_min', 70),
            ('Description', 'Description', 150),
            ('Date', 'Date', 100)
        ]

        for col_id, text, width in columns:
            self.treeview.heading(col_id, text=text)
            self.treeview.column(col_id, width=width, anchor=tk.CENTER)

        # Bind la sélection
        self.treeview.bind('<<TreeviewSelect>>', self.on_tree_select)

    # ===================== LOGIQUE =====================
    def load_initial_data(self):
        categories = get_categories_for_dropdown()

        self.category_map = {}
        category_names = []

        for cat in categories:
            nom = cat['nom_categorie']
            self.category_map[nom] = {
                'id': cat['id_categorie'],
                'seuil': cat['seuil_min_defaut']
            }
            category_names.append(nom)

        self.category_combobox['values'] = category_names
        if category_names:
            self.category_combobox.set(category_names[0])
        else:
            self.category_combobox.set('Select Category')

        self.load_products()

    def load_products(self):
        self.treeview.delete(*self.treeview.get_children())
        products = get_all_products()

        for prod in products:
            self.treeview.insert(
                '',
                tk.END,
                values=(
                    prod['id_produit'],
                    prod['nom_categorie'],
                    prod['nom_produit'],
                    f"{prod['prix_unitaire']:.2f}",
                    prod['quantite_stock'],
                    prod['statut'],
                    prod['seuil_min_personnalise'] or '',
                    (prod['description'][:20] + '...') if prod['description'] and len(prod['description']) > 20 else (
                            prod['description'] or ''),
                    prod['date_ajout'].strftime('%d/%m/%Y') if prod['date_ajout'] else ''
                )
            )

    def on_tree_select(self, event):
        if self.is_clearing:
            return
        
        selection = self.treeview.selection()
        if not selection:
            return
        
        selected = selection[0]

        values = self.treeview.item(selected, 'values')
        if not values or len(values) < 9:
            return

        try:
            product_id = int(values[0])

            if product_id <= 0:
                return

            product = get_product_by_id(product_id)

            if product:
                # Remplir le formulaire
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, product['nom_produit'])

                self.price_entry.delete(0, tk.END)
                self.price_entry.insert(0, str(product['prix_unitaire']))

                self.quantity_entry.config(state='normal')
                self.quantity_entry.delete(0, tk.END)
                self.quantity_entry.insert(0, str(product['quantite_stock']))

                self.statut_combobox.set(product['statut'])

                self.seuil_min_entry.delete(0, tk.END)
                if product['seuil_min_personnalise']:
                    self.seuil_min_entry.insert(0, str(product['seuil_min_personnalise']))

                self.desc_text.delete('1.0', tk.END)
                if product['description']:
                    self.desc_text.insert('1.0', product['description'])

                # Sélectionner la catégorie dans le combobox
                cat_nom = product['nom_categorie']
                if cat_nom in self.category_map:
                    self.category_combobox.set(cat_nom)
                else:
                    self.category_combobox.set(cat_nom)

        except Exception:
            return
        self.quantity_entry.config(state='disabled')

    def validate_form(self):
        # Validation des champs obligatoires
        if not self.name_entry.get().strip():
            messagebox.showwarning("Erreur", "Le nom du produit est obligatoire")
            return False

        if not self.price_entry.get().strip():
            messagebox.showwarning("Erreur", "Le prix est obligatoire")
            return False

        if self.quantity_entry['state'] == 'normal':
            if not self.quantity_entry.get().strip():
                messagebox.showwarning("Erreur", "La quantité est obligatoire")
                return False

        if not self.category_combobox.get() or self.category_combobox.get() == 'Select Category':
            messagebox.showwarning("Erreur", "Veuillez sélectionner une catégorie")
            return False

        if self.statut_combobox.get() == 'Select Statut':
            messagebox.showwarning("Erreur", "Veuillez sélectionner un statut")
            return False

        # Validation des types de données
        try:
            price = float(self.price_entry.get())
            if price <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "Le prix doit être un nombre positif")
            return False

        try:
            quantity = int(self.quantity_entry.get())
            if quantity < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "La quantité doit être un nombre entier positif")
            return False

        if self.seuil_min_entry.get().strip():
            try:
                seuil = int(self.seuil_min_entry.get())
                if seuil < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Erreur", "Le seuil minimum doit être un nombre entier positif")
                return False

        return True

    def get_category_id(self):
        cat = self.category_map.get(self.category_combobox.get())
        return cat['id'] if cat else None

    def add_product(self):
        if not self.validate_form():
            return

        category_id = self.get_category_id()
        if not category_id:
            messagebox.showwarning("Erreur", "Catégorie invalide")
            return

        # Récupération des données
        nom_produit = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        prix_unitaire = float(self.price_entry.get())
        quantite_stock = int(self.quantity_entry.get())
        statut = self.statut_combobox.get()

        seuil_min_personnalise = None
        if self.seuil_min_entry.get().strip():
            seuil_min_personnalise = int(self.seuil_min_entry.get())

        # Appel à la fonction d'ajout
        product_id = add_product(
            nom_produit=nom_produit,
            description=description,
            prix_unitaire=prix_unitaire,
            id_categorie=category_id,
            quantite_stock=quantite_stock,
            seuil_min_personnalise=seuil_min_personnalise,
            statut=statut
        )

        if product_id:
            messagebox.showinfo("Succès", f"Produit ajouté avec l'ID {product_id}")
            self.clear_form()
            self.load_products()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter le produit")

    def update_product(self):
        selected = self.treeview.focus()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un produit à modifier")
            return

        if not self.validate_form():
            return

        values = self.treeview.item(selected, 'values')
        if not values:
            return

        try:
            product_id = int(values[0])
        except (ValueError, IndexError):
            messagebox.showerror("Erreur", "ID de produit invalide")
            return

        category_id = self.get_category_id()

        if not category_id:
            messagebox.showwarning("Erreur", "Catégorie invalide")
            return

        nom_produit = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', tk.END).strip()
        prix_unitaire = float(self.price_entry.get())
        statut = self.statut_combobox.get()

        seuil_min_personnalise = None
        if self.seuil_min_entry.get().strip():
            seuil_min_personnalise = int(self.seuil_min_entry.get())

        if update_product(
                id_produit=product_id,
                nom_produit=nom_produit,
                description=description,
                prix_unitaire=prix_unitaire,
                id_categorie=category_id,
                seuil_min_personnalise=seuil_min_personnalise,
                statut=statut
        ):
            messagebox.showinfo("Succès", "Produit mis à jour")
            self.clear_form()
            self.load_products()
        else:
            messagebox.showerror("Erreur", "Impossible de mettre à jour le produit")

    def delete_product(self):
        selected = self.treeview.focus()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un produit à supprimer")
            return

        values = self.treeview.item(selected, 'values')
        if not values:
            return

        try:
            product_id = int(values[0])
        except (ValueError, IndexError):
            messagebox.showerror("Erreur", "ID de produit invalide")
            return

        if not messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce produit ?"):
            return

        if delete_product(product_id):
            messagebox.showinfo("Succès", "Produit supprimé")
            self.clear_form()
            self.load_products()
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer le produit")

    def search_product(self):
        criterion = self.search_combobox.get()
        keyword = self.search_entry.get().strip()

        if criterion == 'Search By':
            messagebox.showwarning("Attention", "Sélectionnez un critère de recherche")
            return

        if not keyword:
            messagebox.showwarning("Attention", "Entrez un terme de recherche")
            return

        self.treeview.delete(*self.treeview.get_children())
        products = get_all_products()
        filtered_products = []

        for prod in products:
            if criterion == 'Category' and keyword.lower() in prod['nom_categorie'].lower():
                filtered_products.append(prod)
            elif criterion == 'Name' and keyword.lower() in prod['nom_produit'].lower():
                filtered_products.append(prod)
            elif criterion == 'Price':
                try:
                    if float(keyword) == prod['prix_unitaire']:
                        filtered_products.append(prod)
                except ValueError:
                    pass
            elif criterion == 'Quantity':
                try:
                    if int(keyword) == prod['quantite_stock']:
                        filtered_products.append(prod)
                except ValueError:
                    pass
            elif criterion == 'Statut' and keyword.upper() == prod['statut']:
                filtered_products.append(prod)

        for prod in filtered_products:
            self.treeview.insert(
                '',
                tk.END,
                values=(
                    prod['id_produit'],
                    prod['nom_categorie'],
                    prod['nom_produit'],
                    f"{prod['prix_unitaire']:.2f}",
                    prod['quantite_stock'],
                    prod['statut'],
                    prod['seuil_min_personnalise'] or '',
                    (prod['description'][:20] + '...') if prod['description'] and len(prod['description']) > 20 else
                    prod['description'] or '',
                    prod['date_ajout'].strftime('%d/%m/%Y') if prod['date_ajout'] else ''
                )
            )

        if not filtered_products:
            messagebox.showinfo("Info", "Aucun produit trouvé")

    def clear_form(self):
        self.is_clearing = True
        
        # Réactiver quantité pour permettre le delete
        self.quantity_entry.config(state='normal')

        self.name_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.seuil_min_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)

        self.category_combobox.set('Select Category')
        self.statut_combobox.set('Select Statut')

        self.search_entry.delete(0, tk.END)
        self.search_combobox.set('Search By')

        # Réactiver quantité (déjà fait au début mais on s'assure qu'il reste normal pour un nouvel ajout)
        self.quantity_entry.config(state='normal')

        # Désélectionner treeview
        self.treeview.selection_remove(self.treeview.selection())

        self.is_clearing = False

