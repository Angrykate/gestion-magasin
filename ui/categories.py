import tkinter as tk
from tkinter import ttk, messagebox
from db.models import (
    add_category as db_add_category,
    get_all_categories,
    delete_category,
    update_category,
)

class CategorieFrame(tk.Frame):
    def __init__(self, parent,user=None,go_dashboard=None):
        super().__init__(parent, bg='#f8f9fa')
        self.pack(fill=tk.BOTH, expand=True)

        self.create_title()
        self.create_content()
        self.load_categories()

    # ===================== TITRE =====================
    def create_title(self):
        title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        title_bar.pack(fill=tk.X)

        tk.Label(
            title_bar,
            text='Gestion des catégories',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== CONTENU =====================
    def create_content(self):
        content = tk.Frame(self, bg='#f8f9fa')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # --------- GAUCHE : IMAGE ---------
        left_frame = tk.Frame(content, bg='#f8f9fa')
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.category_img = tk.PhotoImage(file="assets/category.png")
        tk.Label(left_frame, image=self.category_img, bg='#f8f9fa').pack(padx=10, pady=10)

        # --------- DROITE : FORMULAIRE + TABLE ---------
        right_frame = tk.Frame(content, bg='#f8f9fa')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --------- FORMULAIRE ---------
        self.form_frame = tk.Frame(right_frame, bg='white', padx=20, pady=20)
        self.form_frame.pack(fill=tk.X)

        # Champs du formulaire
        self.id_entry = tk.Entry(self.form_frame, font=('times new roman', 12), width=25)
        self.id_entry.config(state='readonly')
        self.name_entry = tk.Entry(self.form_frame, font=('times new roman', 12), width=25)
        self.desc_text = tk.Text(self.form_frame, width=25, height=4, font=('times new roman', 12))
        self.seuil_entry = tk.Entry(self.form_frame, font=('times new roman', 12), width=25)

        fields = [
            ('Category ID', self.id_entry),
            ('Category Name', self.name_entry),
            ('Description', self.desc_text),
            ('Seuil Min.', self.seuil_entry)
        ]

        for i, (label_text, widget) in enumerate(fields):
            tk.Label(
                self.form_frame,
                text=label_text,
                font=('times new roman', 12),
                bg='white'
            ).grid(row=i, column=0, sticky='w', pady=8)
            widget.grid(row=i, column=1, pady=8)

        # --------- BOUTONS ---------
        button_frame = tk.Frame(self.form_frame, bg='white')
        button_frame.grid(row=4, column=1, pady=15, sticky='w')

        buttons = [
            ('Add', '#0f4d7d', self.add_category),
            ('Update', '#0d6efd', self.update_category),
            ('Delete', '#dc3545', self.delete_category),
            ('Clear', '#6c757d', self.clear_form)
        ]

        for text, color, cmd in buttons:
            tk.Button(
                button_frame,
                text=text,
                bg=color,
                fg='white',
                font=('times new roman', 11, 'bold'),
                width=8,
                cursor='hand2',
                command=cmd
            ).pack(side=tk.LEFT, padx=5)

        # --------- TABLEAU ---------
        table_frame = tk.Frame(right_frame, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Scrollbars
        v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            table_frame,
            columns=('id', 'name', 'desc', 'seuil_min_defaut'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )

        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        columns = [
            ('id', 'Category ID', 100),
            ('name', 'Category Name', 200),
            ('desc', 'Description', 180),
            ('seuil_min_defaut', 'Seuil Min.', 80)
        ]
        for col, text, width in columns:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=tk.CENTER if col in ('id', 'seuil_min_defaut') else tk.W)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # ===================== LOGIQUE =====================
    def load_categories(self):
        self.tree.delete(*self.tree.get_children())
        for cat in get_all_categories():
            self.tree.insert(
                '',
                tk.END,
                values=(
                    cat['id_categorie'],
                    cat['nom_categorie'],
                    cat['description'],
                    cat['seuil_min_defaut']
                )
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

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])

        self.desc_text.delete('1.0', tk.END)
        self.desc_text.insert(tk.END, values[2])

        self.seuil_entry.delete(0, tk.END)
        self.seuil_entry.insert(0, values[3])

    def add_category(self):
        name = self.name_entry.get()
        desc = self.desc_text.get('1.0', tk.END).strip()
        seuil = self.seuil_entry.get()

        if not name:
            messagebox.showwarning("Erreur", "Le nom est obligatoire")
            return

        try:
            seuil = int(seuil)
            if seuil < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Erreur",
                "Le seuil minimum doit être un nombre entier positif"
            )
            return

        cat_id = db_add_category(name, desc, seuil)
        if cat_id is not None:
            messagebox.showinfo("Succès", f"Catégorie ajoutée (ID {cat_id})")
            self.clear_form()
            self.load_categories()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter la catégorie")

    def update_category(self):
        cat_id = self.id_entry.get()
        name = self.name_entry.get()
        desc = self.desc_text.get('1.0', tk.END).strip()
        seuil = self.seuil_entry.get()
        if not cat_id:
            messagebox.showwarning("Attention", "Sélectionnez une catégorie")
            return
        if not name:
            messagebox.showwarning("Erreur", "Le nom est obligatoire")
            return
        if update_category(cat_id, name, desc, seuil):
            messagebox.showinfo("Succès", "Catégorie mise à jour")
            self.clear_form()
            self.load_categories()
        else:
            messagebox.showerror("Erreur", "Impossible de mettre à jour")
        try:
            seuil = int(seuil)
            if seuil < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Erreur", "Le seuil minimum doit être un nombre positif")
            return

    def delete_category(self):
        cat_id = self.id_entry.get()
        if not cat_id:
            messagebox.showwarning("Attention", "Sélectionnez une catégorie")
            return
        if not messagebox.askyesno("Confirmation", "Supprimer cette catégorie ?"):
            return
        if delete_category(cat_id):
            messagebox.showinfo("Succès", "Catégorie supprimée")
            self.clear_form()
            self.load_categories()
        else:
            messagebox.showerror("Erreur", "Impossible de supprimer")

    def clear_form(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.config(state='readonly')
        self.name_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)
        self.seuil_entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)
