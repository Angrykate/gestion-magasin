import tkinter as tk
from tkinter import ttk, messagebox

from db.models import (
    add_supplier,
    get_all_suppliers,
    delete_supplier,
    update_supplier,
    search_suppliers
)

class FournisseurFrame(tk.Frame):
    def __init__(self, parent,user =None,go_dashboard=None):
        super().__init__(parent, bg='#f8f9fa')
        self.pack(fill=tk.BOTH, expand=True)

        self.create_title()
        self.create_action_bar()
        self.create_content()
        self.load_suppliers()

    # ===================== TITRE =====================
    def create_title(self):
        title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        title_bar.pack(fill=tk.X)

        tk.Label(
            title_bar,
            text='Gestion des fournisseurs',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== BARRE DE RECHERCHE =====================
    def create_action_bar(self):
        bar = tk.Frame(self, bg='white', padx=15, pady=8)
        bar.pack(fill=tk.X)

        tk.Label(bar, text='Nom', font=('times new roman', 12), bg='white').grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(bar, width=30, bg='lightyellow')
        self.search_entry.grid(row=0, column=1, padx=8)

        tk.Button(
            bar,
            text='Search',
            bg='#0f4d7d',
            fg='white',
            font=('times new roman', 12),
            width=10,
            command=self.search_supplier
        ).grid(row=0, column=2, padx=8)

        tk.Button(
            bar,
            text='Show All',
            bg='#6c757d',
            fg='white',
            font=('times new roman', 12),
            width=10,
            command=self.load_suppliers
        ).grid(row=0, column=3, padx=8)

    # ===================== CONTENU =====================
    def create_content(self):
        content = tk.Frame(self, bg='#f8f9fa')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # --------- FORMULAIRE GAUCHE ---------
        self.form_frame = tk.Frame(content, bg='white', padx=20, pady=20)
        self.form_frame.pack(side=tk.LEFT, fill=tk.Y)

        # ID (readonly)
        self.id_entry = tk.Entry(self.form_frame, font=('times new roman', 12), width=30)
        self.id_entry.config(state='readonly')

        self.nom_entry = tk.Entry(self.form_frame, font=('times new roman', 12), width=30)
        self.adresse_text = tk.Text(self.form_frame, font=('times new roman', 12), width=30, height=4)

        fields = [
            ('ID', self.id_entry),
            ('Nom', self.nom_entry),
            ('Adresse', self.adresse_text)
        ]

        for i, (label_text, widget) in enumerate(fields):
            tk.Label(
                self.form_frame,
                text=label_text,
                font=('times new roman', 12),
                bg='white'
            ).grid(row=i, column=0, sticky='w', pady=8)
            widget.grid(row=i, column=1, pady=8)

        # --------- TABLEAU DROITE ---------
        table_frame = tk.Frame(content, bg='white')
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15,0))

        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=('id', 'nom', 'adresse'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        columns = [
            ('id', 'ID', 60),
            ('nom', 'Nom', 150),
            ('adresse', 'Adresse', 250)
        ]

        for col, text, width in columns:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=tk.CENTER)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # --------- BOUTONS CENTRÉS EN BAS ---------
        button_frame = tk.Frame(self, bg='#f8f9fa', pady=12)
        button_frame.pack(fill=tk.X)

        button_container = tk.Frame(button_frame, bg='#f8f9fa')
        button_container.pack()

        buttons = [
            ('Ajouter', '#198754', self.add_supplier),
            ('Update', '#0d6efd', self.update_supplier),
            ('Supprimer', '#dc3545', self.delete_supplier),
            ('Clear', '#6c757d', self.clear_form)
        ]

        for text, color, cmd in buttons:
            tk.Button(
                button_container,
                text=text,
                bg=color,
                fg='white',
                font=('times new roman', 12, 'bold'),
                width=12,
                cursor='hand2',
                command=cmd
            ).pack(side=tk.LEFT, padx=15)

    # ===================== LOGIQUE =====================
    def load_suppliers(self):
        self.tree.delete(*self.tree.get_children())
        for sup in get_all_suppliers():
            self.tree.insert(
                '',
                tk.END,
                values=(
                    sup['id_fournisseur'],
                    sup['nom'],
                    sup['adresse']  # renommer
                )
            )

    def search_supplier(self):
        keyword = self.search_entry.get()
        if not keyword:
            messagebox.showwarning("Attention", "Veuillez entrer un nom à rechercher")
            return
        self.tree.delete(*self.tree.get_children())
        results = search_suppliers(keyword)
        if not results:
            messagebox.showinfo("Info", "Aucun fournisseur trouvé")
            return
        for sup in results:
            self.tree.insert(
                '',
                tk.END,
                values=(sup['id_fournisseur'], sup['nom'], sup['adresse'])
            )

    def on_tree_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, 'values')
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, values[0])
        self.id_entry.config(state='readonly')

        self.nom_entry.delete(0, tk.END)
        self.nom_entry.insert(0, values[1])

        self.adresse_text.delete("1.0", tk.END)
        self.adresse_text.insert("1.0", values[2])

    def add_supplier(self):
        nom = self.nom_entry.get()
        adresse = self.adresse_text.get("1.0", tk.END).strip()
        if not nom:
            messagebox.showwarning("Erreur", "Veuillez remplir le nom")
            return
        supplier_id = add_supplier(nom, adresse)
        if supplier_id is not None:
            messagebox.showinfo("Succès", f"Fournisseur ajouté avec succès (ID {supplier_id})")
            self.clear_form()
            self.load_suppliers()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter le fournisseur")

    def update_supplier(self):
        sup_id = self.id_entry.get()
        nom = self.nom_entry.get()
        adresse = self.adresse_text.get("1.0", tk.END).strip()
        if not sup_id:
            messagebox.showwarning("Attention", "Sélectionnez un fournisseur")
            return
        if not nom:
            messagebox.showwarning("Erreur", "Le nom est obligatoire")
            return
        if update_supplier(sup_id, nom, adresse):
            messagebox.showinfo("Succès", "Fournisseur mis à jour")
            self.clear_form()
            self.load_suppliers()
        else:
            messagebox.showerror("Erreur", "Mise à jour impossible")

    def delete_supplier(self):
        sup_id = self.id_entry.get()
        if not sup_id:
            messagebox.showwarning("Attention", "Sélectionnez un fournisseur")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer ce fournisseur ?"):
            return
        if delete_supplier(sup_id):
            messagebox.showinfo("Succès", "Fournisseur supprimé")
            self.clear_form()
            self.load_suppliers()
        else:
            messagebox.showerror("Erreur", "Suppression impossible")

    def clear_form(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.config(state='readonly')
        self.nom_entry.delete(0, tk.END)
        self.adresse_text.delete("1.0", tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
