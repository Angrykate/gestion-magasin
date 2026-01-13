import tkinter as tk
from tkinter import messagebox
from db.models import authenticate_user


# ===================== Champ mot de passe =====================
class PasswordField(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#e9ecef')

        self.show_image = tk.PhotoImage(file='assets/show.png')
        self.hide_image = tk.PhotoImage(file='assets/hide.png')

        self.entry = tk.Entry(
            self,
            font=('times new roman', 14),
            bg='white',
            show='*',
            relief=tk.FLAT
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        self.toggle_btn = tk.Button(
            self,
            image=self.show_image,
            bd=0,
            bg='white',
            cursor='hand2',
            command=self.show_password
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

    def show_password(self):
        self.entry.config(show='')
        self.toggle_btn.config(image=self.hide_image, command=self.hide_password)

    def hide_password(self):
        self.entry.config(show='*')
        self.toggle_btn.config(image=self.show_image, command=self.show_password)

    def get(self):
        return self.entry.get()


# ===================== LoginFrame =====================
class LoginFrame(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg='white')
        self.on_login_success = on_login_success

        self.create_header()
        self.create_content()

    # ===================== HEADER =====================
    def create_header(self):
        tk.Label(
            self,
            text='Système de gestion de magasin',
            font=('times new roman', 36, 'bold'),
            bg='#010c48',
            fg='white',
            pady=20
        ).pack(fill=tk.X)

    # ===================== CONTENT =====================
    def create_content(self):
        content = tk.Frame(self, bg='white')
        content.pack(fill=tk.BOTH, expand=True)

        # Image gauche
        self.side_image = tk.PhotoImage(file='assets/vector.png')
        tk.Label(content, image=self.side_image, bg='white').place(x=30, y=50)

        # Carte login
        card = tk.Frame(content, bg='#e9ecef', width=360, height=460)
        card.place(x=680, y=40)
        card.pack_propagate(False)

        self.login_icon = tk.PhotoImage(file='assets/login.png')
        tk.Label(card, image=self.login_icon, bg='#e9ecef').pack(pady=(30, 10))

        tk.Label(
            card,
            text="Connexion",
            font=('times new roman', 22, 'bold'),
            bg='#e9ecef',
            fg='#010c48'
        ).pack(pady=(0, 25))

        # Email
        tk.Label(card, text="Email", bg='#e9ecef', font=('times new roman', 14)).pack(fill=tk.X, padx=40)
        self.email_entry = tk.Entry(card, font=('times new roman', 14), relief=tk.FLAT)
        self.email_entry.pack(fill=tk.X, padx=40, pady=(5, 20), ipady=6)

        # Password
        tk.Label(card, text="Mot de passe", bg='#e9ecef', font=('times new roman', 14)).pack(fill=tk.X, padx=40)
        self.password_field = PasswordField(card)
        self.password_field.pack(fill=tk.X, padx=40, pady=(5, 0))

        # Forgot password
        tk.Button(
            card,
            text="Mot de passe oublié ?",
            font=('times new roman', 11, 'underline'),
            bg='#e9ecef',
            fg='#0d6efd',
            bd=0,
            cursor='hand2',
            command=self.forgot_password
        ).pack(anchor='w', padx=40, pady=(4, 15))

        # Login button
        tk.Button(
            card,
            text="Se connecter",
            font=('times new roman', 15, 'bold'),
            bg='#010c48',
            fg='white',
            bd=0,
            cursor='hand2',
            command=self.login
        ).pack(fill=tk.X, padx=40, ipady=8)

        # Footer
        tk.Label(
            card,
            text="© 2026 - Système de gestion",
            font=('times new roman', 10),
            bg='#e9ecef',
            fg='#6c757d'
        ).pack(side=tk.BOTTOM, pady=10)

    # ===================== ACTIONS =====================
    def login(self):
        email = self.email_entry.get()
        password = self.password_field.get()

        if not email or not password:
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs")
            return

        user = authenticate_user(email, password)

        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Connexion échouée", "Identifiants incorrects")

    def forgot_password(self):
        messagebox.showinfo(
            "Mot de passe oublié",
            "Veuillez contacter l'administrateur du système\n"
        "pour réinitialiser votre mot de passe."
        )
