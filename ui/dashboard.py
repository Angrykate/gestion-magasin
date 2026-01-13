import tkinter as tk


class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#e9ecef')
        self.pack(fill=tk.BOTH, expand=True)

        self.create_title()
        self.create_kpis()
        self.create_charts()
        self.create_quick_actions()

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

        self.create_kpi(container, 0,   "Chiffre d'affaires du jour", "0")
        self.create_kpi(container, 260, "Nombre de ventes du jour", "0")
        self.create_kpi(container, 520, "Produits en seuil bas", "0")
        self.create_kpi(container, 780, "Nombre total de produits", "0")

    def create_kpi(self, parent, x, title, value):
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

        # TITRE (ligne 0)
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

        # VALEUR (ligne 1)
        value_label = tk.Label(
            frame,
            text=value,
            font=('times new roman', 22, 'bold'),
            bg='white',
            fg='#212529'
        )
        value_label.grid(row=1, column=0, sticky='w', padx=15, pady=(0, 10))

    # ===================== ZONES GRAPHIQUES =====================
    def create_charts(self):
        container = tk.Frame(self, bg='#f5f6f8')
        container.place(x=20, y=210, width=1030, height=260)

        self.create_chart_placeholder(
            container,
            x=0,
            title="Ventes par mois"
        )

        self.create_chart_placeholder(
            container,
            x=530,
            title="Répartition des produits par catégorie"
        )

    def create_chart_placeholder(self, parent, x, title):
        frame = tk.Frame(
            parent,
            bg='white',
            highlightbackground='#ced4da',
            highlightthickness=1
        )
        frame.place(x=x, y=0, width=500, height=260)

        tk.Label(
            frame,
            text=title,
            font=('times new roman', 15, 'bold'),
            bg='#d3d3d3',
            fg='#212529',
            anchor='w',
            padx=10
        ).place(x=0, y=0, relwidth=1, height=40)

        tk.Label(
            frame,
            text="(Visualisation à venir)",
            font=('times new roman', 12, 'italic'),
            bg='white',
            fg='#6c757d'
        ).place(relx=0.5, rely=0.5, anchor='center')

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

        tk.Button(
            frame,
            text="Ajouter un produit",
            bg='#0d6efd',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2'
        ).place(x=120, y=15)

        tk.Button(
            frame,
            text="Passer une vente",
            bg='#198754',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2'
        ).place(x=360, y=15)

        tk.Button(
            frame,
            text="Voir rapports",
            bg='#343a40',
            fg='white',
            font=('times new roman', 13, 'bold'),
            bd=0,
            padx=15,
            cursor='hand2'
        ).place(x=600, y=15)
