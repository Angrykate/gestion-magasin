import tkinter as tk
from tkinter import ttk, messagebox

from db.models import (
    add_employee,
    get_all_employees,
    delete_employee as db_delete_employee,
    update_employee as db_update_employee,
    search_employees
)


class EmployeFrame(tk.Frame):
    def __init__(self, parent,user=None,go_dashboard=None):
        super().__init__(parent, bg='#f8f9fa')
        self.pack(fill=tk.BOTH, expand=True)

        self.create_title()
        self.create_action_bar()
        self.create_table()
        self.create_form()
        self.load_employees()

    # ===================== TITRE =====================
    def create_title(self):
        title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        title_bar.pack(fill=tk.X)

        tk.Label(
            title_bar,
            text='Gestion des employés',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== ACTION BAR =====================
    def create_action_bar(self):
        bar = tk.Frame(self, bg='white', padx=15, pady=8)
        bar.pack(fill=tk.X)

        self.search_cb = ttk.Combobox(
            bar,
            values=('Nom', 'Email', 'Rôle'),
            state='readonly',
            font=('times new roman',12),
            width=12
        )
        # self.search_cb.set('Nom')
        self.search_cb.set('Search By')
        self.search_cb.grid(row=0, column=0, padx=8)

        self.search_entry = tk.Entry(bar, width=30, bg='lightyellow')
        self.search_entry.grid(row=0, column=1, padx=8)

        tk.Button(
            bar,
            text='Search',
            bg='#0f4d7d',
            fg='white',
            font=('times new roman', 12),
            width=10,
            command=self.search_employee
        ).grid(row=0, column=2, padx=8)

        tk.Button(
            bar,
            text='Show All',
            bg='#6c757d',
            fg='white',
            font=('times new roman', 12),
            width=10,
            command=self.load_employees
        ).grid(row=0, column=3, padx=8)

    # ===================== TABLE =====================
    def create_table(self):
        table_frame = tk.Frame(self, bg='white')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            table_frame,
            columns=('id', 'nom', 'email', 'password', 'role'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.tree.yview)

        columns = [
            ('id', 'ID', 60),
            ('nom', 'Nom', 150),
            ('email', 'Email', 200),
            ('password', 'Mot de passe', 150),
            ('role', 'Rôle', 150)
        ]

        for col, text, width in columns:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=tk.CENTER)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    # ===================== FORMULAIRE =====================
    def create_form(self):
        form = tk.Frame(self, bg='white', padx=20, pady=12)
        form.pack(fill=tk.X, padx=15)

        # ===================== ENTRIES =====================
        self.id_entry = tk.Entry(form, font=('times new roman', 12), width=30)
        self.id_entry.config(state='readonly')

        self.nom_entry = tk.Entry(form, font=('times new roman', 12), width=30)
        self.email_entry = tk.Entry(form, font=('times new roman', 12), width=30)
        self.pass_entry = tk.Entry(form, font=('times new roman', 12), width=30, show='*')

        self.role_cb = ttk.Combobox(
            form,
            values=('CAISSIER', 'GESTIONNAIRE_STOCK', 'RESPONSABLE_ACHAT'),
            state='readonly',
            width=28
        )
        self.role_cb.set('Sélectionner un rôle')

        fields = [
            ('ID', self.id_entry),
            ('Nom', self.nom_entry),
            ('Email', self.email_entry),
            ('Mot de passe', self.pass_entry),
            ('Rôle', self.role_cb)
        ]

        for i, (label_text, widget) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(
                form,
                text=label_text,
                font=('times new roman', 12),
                bg='white'
            ).grid(row=row, column=col, sticky='w', padx=10, pady=6)

            widget.grid(row=row, column=col + 1, padx=10, pady=6)

        # ===================== BOUTONS =====================
        button_frame = tk.Frame(self, bg='#f8f9fa', pady=12)
        button_frame.pack(fill=tk.X)

        button_container = tk.Frame(button_frame, bg='#f8f9fa')
        button_container.pack()

        buttons = [
            ('Ajouter', '#198754', self.add_employee),
            ('Update', '#0d6efd', self.update_employee),
            ('Supprimer', '#dc3545', self.delete_employee),
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
    def on_tree_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        selected = selection[0]
        values = self.tree.item(selected, 'values')

        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, values[0])
        self.id_entry.config(state='readonly')

        self.nom_entry.delete(0, tk.END)
        self.nom_entry.insert(0, values[1])

        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, values[2])

        self.pass_entry.delete(0, tk.END)
        self.role_cb.set(values[4])

    def add_employee(self):
        nom = self.nom_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        role = self.role_cb.get()

        if not nom or not email or not password or role == 'Sélectionner un rôle':
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs")
            return

        if add_employee(nom, email, password, role):
            messagebox.showinfo("Succès", "Employé ajouté avec succès")
            self.clear_form()
            self.load_employees()
        else:
            messagebox.showerror("Erreur", "Impossible d'ajouter l'employé")

    def load_employees(self):
        self.tree.delete(*self.tree.get_children())

        for emp in get_all_employees():
            self.tree.insert(
                '',
                tk.END,
                values=(
                    emp['id_utilisateur'],
                    emp['nom'],
                    emp['email'],
                    '********',
                    emp['role']
                )
            )

    def search_employee(self):
        field_map = {
            'role': 'role',
            'Nom': 'nom',
            'Email': 'email'
        }

        search_by = self.search_cb.get()
        keyword = self.search_entry.get()

        if search_by not in field_map or not keyword:
            messagebox.showwarning(
                "Attention",
                "Choisissez un critère et entrez une valeur"
            )
            return

        self.tree.delete(*self.tree.get_children())

        results = search_employees(field_map[search_by], keyword)

        if not results:
            messagebox.showinfo("Info", "Aucun résultat trouvé")
            return

        for emp in results:
            self.tree.insert(
                '',
                tk.END,
                values=(
                    emp['id_utilisateur'],
                    emp['nom'],
                    emp['email'],
                    '********',
                    emp['role']
                )
            )

    def delete_employee(self):
        emp_id = self.id_entry.get()
        if not emp_id:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return

        if not messagebox.askyesno("Confirmation", "Supprimer cet employé ?"):
            return

        if db_delete_employee(emp_id):
            messagebox.showinfo("Succès", "Employé supprimé")
            self.clear_form()
            self.load_employees()
        else:
            messagebox.showerror("Erreur", "Suppression impossible")

    def update_employee(self):
        emp_id = self.id_entry.get()
        nom = self.nom_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        role = self.role_cb.get()

        if not emp_id:
            messagebox.showwarning("Attention", "Sélectionnez un employé")
            return

        if not nom or not email or role == 'Sélectionner un rôle':
            messagebox.showwarning("Erreur", "Champs obligatoires manquants")
            return

        if db_update_employee(emp_id, nom, email, password, role):
            messagebox.showinfo("Succès", "Employé mis à jour")
            self.clear_form()
            self.load_employees()
        else:
            messagebox.showerror("Erreur", "Mise à jour impossible")

    def clear_form(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.id_entry.config(state='readonly')

        self.nom_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.role_cb.set('Sélectionner un rôle')
        for item in self.tree.selection():
            self.tree.selection_remove(item)
