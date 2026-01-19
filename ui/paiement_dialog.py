import tkinter as tk
from tkinter import ttk, messagebox


class PaiementDialog:
    def __init__(self, parent, total_vente, callback):
        """
        parent: fenêtre parente
        total_vente: montant total à payer
        callback: fonction à appeler après paiement (succès, montant_recu, mode)
        """
        self.parent = parent
        self.total_vente = total_vente
        self.callback = callback

        self.create_dialog()

    def create_dialog(self):
        """Crée la fenêtre modale"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("💳 Paiement de la vente")
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='white')

        # Centrer la fenêtre
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Empêcher la fermeture avec la croix sans confirmation
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_content()

    def create_content(self):
        """Crée le contenu de la fenêtre"""
        
        # ===== BOUTONS (Packed FIRST at BOTTOM for visibility) =====
        btn_frame = tk.Frame(self.dialog, bg='white', pady=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=30, pady=10)

        self.valider_btn = tk.Button(
            btn_frame,
            text="✅ VALIDER L'ENCAISSEMENT",
            font=('times new roman', 13, 'bold'),
            bg='#198754',
            fg='white',
            bd=0,
            cursor='hand2',
            state='disabled',
            command=self.on_validate
        )
        self.valider_btn.pack(fill=tk.X, ipady=10, pady=(0, 5))

        tk.Button(
            btn_frame,
            text="Annuler",
            font=('times new roman', 11),
            bg='#f8f9fa',
            fg='#6c757d',
            bd=0,
            cursor='hand2',
            command=self.on_cancel
        ).pack(fill=tk.X)

        # ===== CONTENU PRINCIPAL =====
        main_content = tk.Frame(self.dialog, bg='white')
        main_content.pack(fill=tk.BOTH, expand=True)

        # ===== TITRE =====
        tk.Label(
            main_content,
            text="ENCAISSEMENT",
            font=('times new roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white',
            pady=15
        ).pack(fill=tk.X)

        # ===== MONTANT TOTAL =====
        total_frame = tk.Frame(main_content, bg='white', pady=20)
        total_frame.pack(fill=tk.X, padx=20)

        tk.Label(
            total_frame,
            text="TOTAL À PAYER",
            font=('times new roman', 12),
            bg='white',
            fg='#6c757d'
        ).pack()

        self.total_label = tk.Label(
            total_frame,
            text=f"{self.total_vente:,.0f} FCFA",
            font=('times new roman', 30, 'bold'),
            bg='white',
            fg='#212529'
        )
        self.total_label.pack(pady=5)

        # Séparateur
        tk.Frame(main_content, height=2, bg='#e9ecef').pack(fill=tk.X, padx=30, pady=10)

        # ===== SAISIE MONTANT REÇU =====
        input_container = tk.Frame(main_content, bg='white', pady=10)
        input_container.pack(fill=tk.X, padx=30)

        tk.Label(
            input_container,
            text="Montant reçu (FCFA) :",
            font=('times new roman', 12, 'bold'),
            bg='white',
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        self.montant_entry = tk.Entry(
            input_container,
            font=('times new roman', 20),
            bg='#f8f9fa',
            justify='right',
            bd=1,
            relief=tk.SOLID
        )
        self.montant_entry.pack(fill=tk.X, ipady=5)
        self.montant_entry.focus()
        self.montant_entry.bind('<KeyRelease>', self.calculer_monnaie)
        self.montant_entry.bind('<Return>', lambda e: self.on_validate())

        # ===== MONNAIE À RENDRE =====
        monnaie_frame = tk.Frame(main_content, bg='#e8f5e9', pady=20, padx=15, bd=2, relief=tk.GROOVE)
        monnaie_frame.pack(fill=tk.X, padx=30, pady=20)

        tk.Label(
            monnaie_frame,
            text="MONNAIE À RENDRE :",
            font=('times new roman', 14, 'bold'),
            bg='#e8f5e9',
            fg='#198754'
        ).pack(anchor='w')

        self.monnaie_label = tk.Label(
            monnaie_frame,
            text="0 FCFA",
            font=('times new roman', 45, 'bold'),
            bg='#e8f5e9',
            fg='#198754'
        )
        self.monnaie_label.pack(pady=(5, 0))

        self.error_label = tk.Label(
            main_content,
            text="",
            font=('times new roman', 10, 'italic'),
            bg='white',
            fg='#dc3545'
        )
        self.error_label.pack(pady=(0, 10))

    def calculer_monnaie(self, event=None):
        """Calcule la monnaie à rendre en temps réel"""
        texte = self.montant_entry.get().strip()
        if not texte:
            self.monnaie_label.config(text="0 FCFA", fg='#6c757d')
            self.valider_btn.config(state='disabled', bg='#6c757d')
            return

        try:
            # Remplacement pour éviter erreurs de format
            montant_recu = float(texte.replace(' ', '').replace(',', '.'))
            
            if montant_recu >= self.total_vente:
                monnaie = montant_recu - self.total_vente
                self.monnaie_label.config(
                    text=f"{monnaie:,.0f} FCFA", 
                    fg='#198754'
                )
                self.error_label.config(text="")
                self.valider_btn.config(state='normal', bg='#198754')
            else:
                self.monnaie_label.config(text="Montant insuffisant", fg='#dc3545')
                self.error_label.config(text=f"Manque : {self.total_vente - montant_recu:,.0f} FCFA")
                self.valider_btn.config(state='disabled', bg='#6c757d')

        except ValueError:
            self.monnaie_label.config(text="Erreur saisie", fg='#dc3545')
            self.valider_btn.config(state='disabled', bg='#6c757d')

    def on_validate(self):
        """Valide le paiement"""
        if self.valider_btn['state'] == 'disabled':
            return

        try:
            montant_recu = float(self.montant_entry.get().replace(' ', '').replace(',', '.'))
            self.dialog.destroy()
            # On retourne True, le montant reçu, et le mode 'ESPECES' forcé
            self.callback(True, montant_recu, 'ESPECES')
        except ValueError:
            pass

    def on_cancel(self):
        """Annule"""
        self.dialog.destroy()
        self.callback(False, None, None)

    def on_close(self):
        """Demande confirmation avant de fermer"""
        if messagebox.askyesno("Annuler", "Voulez-vous annuler l'encaissement ?"):
            self.on_cancel()