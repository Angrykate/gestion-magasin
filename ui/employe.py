import tkinter as tk
from tkinter import ttk, messagebox


class EmployeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#f8f9fa')
        self.pack(fill=tk.BOTH, expand=True)

        self.create_title()
        self.create_action_bar()
        self.create_table()
        self.create_form()
        self.create_buttons()

    # ===================== TITRE =====================
    def create_title(self):
        title_bar = tk.Frame(self, bg='#0f4d7d', height=50)
        title_bar.pack(fill=tk.X)

        tk.Label(
            title_bar,
            text='Gestion des employés',
            font=('times new roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== ACTION BAR =====================
    def create_action_bar(self):
        bar = tk.Frame(self, bg='white', padx=15, pady=8)
        bar.pack(fill=tk.X)

        self.search_cb = ttk.Combobox(
            bar,
            values=('Id', 'Nom', 'Email'),
            state='readonly',
            width=12
        )
        self.search_cb.set('Search By')
        self.search_cb.grid(row=0, column=0, padx=8)

        self.search_entry = tk.Entry(bar, width=30, bg='lightyellow')
        self.search_entry.grid(row=0, column=1, padx=8)

        tk.Button(
            bar, text='Search',
            bg='#0f4d7d', fg='white',
            width=10
        ).grid(row=0, column=2, padx=8)

        tk.Button(
            bar, text='Show All',
            bg='#6c757d', fg='white',
            width=10
        ).grid(row=0, column=3, padx=8)

    # ===================== TABLE =====================
    def create_table(self):
        container = tk.Frame(self, bg='white')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        scrollbar = tk.Scrollbar(container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            container,
            columns=('id', 'nom', 'email', 'role'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        for col, txt, w in [
            ('id', 'ID', 80),
            ('nom', 'Nom', 180),
            ('email', 'Email', 220),
            ('role', 'Rôle', 150)
        ]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor=tk.CENTER)

    # ===================== FORM =====================
    def create_form(self):
        form = tk.Frame(self, bg='white', padx=20, pady=12)
        form.pack(fill=tk.X, padx=15)

        labels = ['Nom', 'Email', 'Mot de passe', 'Rôle']
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(
                form, text=label,
                bg='white',
                font=('times new roman', 12)
            ).grid(row=i//2, column=(i % 2)*2, sticky='w', padx=10, pady=6)

            if label == 'Rôle':
                entry = ttk.Combobox(
                    form,
                    values=('CAISSIER', 'GESTIONNAIRE_STOCK'),
                    state='readonly',
                    width=28
                )
                entry.set('Choisir rôle')
            else:
                entry = tk.Entry(
                    form,
                    bg='lightyellow',
                    width=30
                )

            entry.grid(row=i//2, column=(i % 2)*2 + 1, padx=10, pady=6)
            self.entries[label] = entry

    # ===================== BUTTONS =====================
    def create_buttons(self):
        frame = tk.Frame(self, bg='#f8f9fa', pady=12)
        frame.pack(fill=tk.X)

        container = tk.Frame(frame, bg='#f8f9fa')
        container.pack()

        for text, color in [
            ('Add', '#198754'),
            ('Update', '#0d6efd'),
            ('Delete', '#dc3545'),
            ('Clear', '#6c757d')
        ]:
            tk.Button(
                container,
                text=text,
                bg=color,
                fg='white',
                width=12,
                font=('times new roman', 12, 'bold'),
                cursor='hand2'
            ).pack(side=tk.LEFT, padx=15)
