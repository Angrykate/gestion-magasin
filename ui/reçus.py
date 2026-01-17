import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from db.models import get_connection, get_cursor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import tempfile


class ReçusFrame(tk.Frame):
    def __init__(self, parent, user=None, go_dashboard=None):
        super().__init__(parent, bg='#f5f6f8')
        self.pack(fill=tk.BOTH, expand=True)

        self.user = user
        self.go_dashboard = go_dashboard
        self.current_receipt = None

        self.create_title()
        self.create_left_panel()
        self.create_right_panel()

        # Charger les reçus
        self.load_receipts()

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
            text='🧾 Gestion des Reçus',
            font=('Times New Roman', 18, 'bold'),
            bg='#0f4d7d',
            fg='white'
        ).pack(expand=True)

    # ===================== PANEL GAUCHE - LISTE DES REÇUS =====================
    def create_left_panel(self):
        left_frame = tk.Frame(self, bg='white', bd=2, relief=tk.RIDGE)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 5), pady=10)

        # Titre
        tk.Label(
            left_frame,
            text='📋 Liste des reçus',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 10))

        # Barre de recherche
        search_frame = tk.Frame(left_frame, bg='white')
        search_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            search_frame,
            text='Rechercher:',
            font=('times new roman', 10),
            bg='white'
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = tk.Entry(
            search_frame,
            font=('times new roman', 10),
            bg='lightyellow',
            width=20
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.search_receipts)

        tk.Button(
            search_frame,
            text='🔄',
            font=('times new roman', 10, 'bold'),
            bg='#6c757d',
            fg='white',
            cursor='hand2',
            width=3,
            command=self.load_receipts
        ).pack(side=tk.LEFT)

        # Treeview des reçus
        tree_frame = tk.Frame(left_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbars
        v_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        self.receipts_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Vente', 'Date', 'Montant', 'Client'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=15
        )

        v_scrollbar.config(command=self.receipts_tree.yview)
        h_scrollbar.config(command=self.receipts_tree.xview)

        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.receipts_tree.pack(fill=tk.BOTH, expand=True)

        # Configuration des colonnes
        columns = [
            ('ID', 'ID Recu', 60),
            ('Vente', 'N° Vente', 70),
            ('Date', 'Date', 120),
            ('Montant', 'Montant', 90),
            ('Client', 'Client', 120)
        ]

        for col, text, width in columns:
            self.receipts_tree.heading(col, text=text)
            self.receipts_tree.column(col, width=width, anchor=tk.CENTER if col in ('ID', 'Vente', 'Montant') else tk.W)

        # Bind la sélection
        self.receipts_tree.bind('<<TreeviewSelect>>', self.on_receipt_select)

    # ===================== PANEL DROIT - DÉTAIL DU REÇU =====================
    def create_right_panel(self):
        right_frame = tk.Frame(self, bg='white', bd=2, relief=tk.RIDGE)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 20), pady=10)

        # Titre
        tk.Label(
            right_frame,
            text='📄 Détail du reçu',
            font=('times new roman', 12, 'bold'),
            bg='#e9ecef',
            anchor='w',
            padx=10
        ).pack(fill=tk.X, pady=(0, 15))

        # Zone d'affichage du reçu
        receipt_display_frame = tk.Frame(right_frame, bg='white', bd=1, relief=tk.SUNKEN)
        receipt_display_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Text widget pour afficher le reçu
        self.receipt_text = tk.Text(
            receipt_display_frame,
            font=('Courier', 10),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            height=20,
            width=50
        )

        # Scrollbar pour le text widget
        text_scrollbar = tk.Scrollbar(receipt_display_frame, orient=tk.VERTICAL)
        text_scrollbar.config(command=self.receipt_text.yview)
        self.receipt_text.config(yscrollcommand=text_scrollbar.set)

        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.receipt_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Message par défaut
        self.receipt_text.insert(tk.END, "Sélectionnez un reçu à gauche\npour voir son contenu ici")
        self.receipt_text.config(state='disabled')

        # Boutons d'action
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        tk.Button(
            button_frame,
            text='📄 Générer TXT',
            font=('times new roman', 11, 'bold'),
            bg='#0d6efd',
            fg='white',
            cursor='hand2',
            width=15,
            command=self.generate_txt_receipt
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text='📊 Générer PDF',
            font=('times new roman', 11, 'bold'),
            bg='#dc3545',
            fg='white',
            cursor='hand2',
            width=15,
            command=self.generate_pdf_receipt
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text='🖨 Imprimer',
            font=('times new roman', 11, 'bold'),
            bg='#198754',
            fg='white',
            cursor='hand2',
            width=15,
            command=self.print_receipt
        ).pack(side=tk.LEFT, padx=5)

    # ===================== LOGIQUE =====================
    def load_receipts(self):
        """Charge la liste des reçus depuis la base"""
        self.receipts_tree.delete(*self.receipts_tree.get_children())

        conn = get_connection()
        if not conn:
            messagebox.showerror("Erreur", "Connexion BD impossible")
            return

        cur = get_cursor(conn)
        try:
            # Récupérer les reçus avec infos vente
            query = """
                SELECT 
                    r.id_recu,
                    r.id_vente,
                    r.date_recu,
                    r.montant_total,
                    u.nom as vendeur,
                    v.total_vente
                FROM recu r
                JOIN vente v ON r.id_vente = v.id_vente
                JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
            """
            
            params = []
            if self.user['role'] != 'ADMIN':
                query += " WHERE v.id_utilisateur = %s"
                params.append(self.user['id_utilisateur'])
                
            query += " ORDER BY r.date_recu DESC"
            
            cur.execute(query, tuple(params))

            receipts = cur.fetchall()

            for rec in receipts:
                date_str = rec['date_recu'].strftime("%d/%m/%Y %H:%M")
                montant = f"{rec['montant_total']:,.2f} €"

                self.receipts_tree.insert(
                    '',
                    tk.END,
                    values=(
                        rec['id_recu'],
                        rec['id_vente'],
                        date_str,
                        montant,
                        rec['vendeur']
                    )
                )

        except Exception as e:
            print(f"Erreur load_receipts: {e}")
            messagebox.showerror("Erreur", f"Impossible de charger les reçus: {e}")
        finally:
            cur.close()
            conn.close()

    def search_receipts(self, event=None):
        """Filtre les reçus selon la recherche"""
        keyword = self.search_entry.get().strip().lower()

        # Cacher toutes les lignes
        for item in self.receipts_tree.get_children():
            self.receipts_tree.item(item, tags=())

        # Montrer seulement ceux qui correspondent
        for item in self.receipts_tree.get_children():
            values = self.receipts_tree.item(item, 'values')
            if any(keyword in str(value).lower() for value in values):
                self.receipts_tree.item(item, tags=('visible',))
            else:
                self.receipts_tree.detach(item)

    def on_receipt_select(self, event):
        """Affiche le détail d'un reçu sélectionné"""
        selected = self.receipts_tree.focus()
        if not selected:
            return

        values = self.receipts_tree.item(selected, 'values')
        if not values:
            return

        receipt_id = int(values[0])

        # Charger les détails du reçu
        self.load_receipt_details(receipt_id)

    def load_receipt_details(self, receipt_id):
        """Charge et affiche le détail d'un reçu"""
        conn = get_connection()
        if not conn:
            return

        cur = get_cursor(conn)
        try:
            # Récupérer les détails complets
            cur.execute("""
                SELECT 
                    r.id_recu,
                    r.date_recu,
                    r.montant_total,
                    v.id_vente,
                    v.date_vente,
                    u.nom as vendeur,
                    u.role
                FROM recu r
                JOIN vente v ON r.id_vente = v.id_vente
                JOIN utilisateur u ON v.id_utilisateur = u.id_utilisateur
                WHERE r.id_recu = %s
            """, (receipt_id,))

            receipt_info = cur.fetchone()

            if not receipt_info:
                return

            # Récupérer les lignes de vente
            cur.execute("""
                SELECT 
                    p.nom_produit,
                    lv.quantite_vendue,
                    lv.prix_unitaire,
                    (lv.quantite_vendue * lv.prix_unitaire) as total_ligne
                FROM ligne_vente lv
                JOIN produit p ON lv.id_produit = p.id_produit
                WHERE lv.id_vente = %s
                ORDER BY p.nom_produit
            """, (receipt_info['id_vente'],))

            items = cur.fetchall()

            # Stocker les infos pour génération
            self.current_receipt = {
                'id': receipt_info['id_recu'],
                'vente_id': receipt_info['id_vente'],
                'date': receipt_info['date_recu'],
                'montant': receipt_info['montant_total'],
                'vendeur': receipt_info['vendeur'],
                'role_vendeur': receipt_info['role'],
                'items': items
            }

            # Générer l'affichage texte
            self.display_receipt_text(receipt_info, items)

        except Exception as e:
            print(f"Erreur load_receipt_details: {e}")
        finally:
            cur.close()
            conn.close()

    def display_receipt_text(self, receipt_info, items):
        """Affiche le reçu formaté dans le Text widget"""
        # Effacer le contenu précédent
        self.receipt_text.config(state='normal')
        self.receipt_text.delete(1.0, tk.END)

        # Construire le reçu
        lines = []
        lines.append("=" * 40)
        lines.append("         REÇU DE VENTE")
        lines.append("=" * 40)
        lines.append(f"Vente N° : {receipt_info['id_vente']}")
        lines.append(f"Date     : {receipt_info['date_recu'].strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Vendeur  : {receipt_info['vendeur']} ({receipt_info['role']})")
        lines.append(f"Recu N°  : {receipt_info['id_recu']}")
        lines.append("-" * 40)
        lines.append(f"{'Produit':<20} {'Qté':>5} {'PU':>8} {'Total':>10}")
        lines.append("-" * 40)

        total_general = 0
        for item in items:
            nom = item['nom_produit'][:19]  # Limiter la longueur
            qte = item['quantite_vendue']
            pu = item['prix_unitaire']
            total = item['total_ligne']
            total_general += total

            lines.append(f"{nom:<20} {qte:>5} {pu:>8.2f} {total:>10.2f}")

        lines.append("-" * 40)
        lines.append(f"{'TOTAL À PAYER :':<33} {total_general:>10.2f} €")
        lines.append("=" * 40)
        lines.append("Merci pour votre confiance !")
        lines.append("=" * 40)

        # Insérer dans le Text widget
        for line in lines:
            self.receipt_text.insert(tk.END, line + "\n")

        # Centrer le texte
        self.receipt_text.tag_configure("center", justify='center')
        self.receipt_text.tag_add("center", "1.0", "end")

        # Désactiver l'édition
        self.receipt_text.config(state='disabled')

    def generate_txt_receipt(self):
        """Génère un fichier TXT du reçu"""
        if not self.current_receipt:
            messagebox.showwarning("Attention", "Aucun reçu sélectionné")
            return

        # Demander où sauvegarder
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous fichiers", "*.*")],
            initialfile=f"recu_{self.current_receipt['id']}.txt"
        )

        if not file_path:
            return

        try:
            # Récupérer le texte du widget
            self.receipt_text.config(state='normal')
            receipt_content = self.receipt_text.get(1.0, tk.END)
            self.receipt_text.config(state='disabled')

            # Sauvegarder dans le fichier
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(receipt_content)

            messagebox.showinfo("Succès", f"Reçu sauvegardé sous:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder: {e}")

    def generate_pdf_receipt(self):
        """Génère un fichier PDF du reçu"""
        if not self.current_receipt:
            messagebox.showwarning("Attention", "Aucun reçu sélectionné")
            return

        # Demander où sauvegarder
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous fichiers", "*.*")],
            initialfile=f"recu_{self.current_receipt['id']}.pdf"
        )

        if not file_path:
            return

        try:
            # Créer le PDF
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            # Titre
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 50, "REÇU DE VENTE")

            c.setFont("Helvetica", 10)

            # Infos reçu
            y = height - 80
            c.drawString(50, y, f"Vente N° : {self.current_receipt['vente_id']}")
            c.drawString(width / 2, y, f"Reçu N° : {self.current_receipt['id']}")

            y -= 20
            c.drawString(50, y, f"Date     : {self.current_receipt['date'].strftime('%Y-%m-%d %H:%M')}")

            y -= 20
            c.drawString(50, y, f"Vendeur  : {self.current_receipt['vendeur']}")

            # Ligne séparatrice
            y -= 30
            c.line(50, y, width - 50, y)

            # En-tête tableau
            y -= 20
            c.drawString(50, y, "Produit")
            c.drawString(width - 300, y, "Qté")
            c.drawString(width - 250, y, "P.U.")
            c.drawString(width - 150, y, "Total")

            y -= 10
            c.line(50, y, width - 50, y)

            # Articles
            y -= 20
            for item in self.current_receipt['items']:
                nom = item['nom_produit']
                if len(nom) > 30:
                    nom = nom[:27] + "..."

                c.drawString(50, y, nom)
                c.drawString(width - 300, y, str(item['quantite_vendue']))
                c.drawString(width - 250, y, f"{item['prix_unitaire']:.2f}")
                c.drawString(width - 150, y, f"{item['total_ligne']:.2f}")
                y -= 20

                # Nouvelle page si nécessaire
                if y < 100:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 50

            # Ligne séparatrice
            c.line(50, y, width - 50, y)

            # Total
            y -= 30
            c.setFont("Helvetica-Bold", 12)
            c.drawString(width - 200, y, "TOTAL À PAYER :")
            c.drawString(width - 150, y, f"{self.current_receipt['montant']:.2f} €")

            # Pied de page
            y -= 50
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width / 2, y, "Merci pour votre confiance !")

            # Signature
            y -= 40
            c.line(width - 200, y, width - 50, y)
            c.drawString(width - 150, y - 15, "Signature")

            c.save()

            messagebox.showinfo("Succès", f"PDF généré sous:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le PDF: {e}")

    def print_receipt(self):
        """Imprime le reçu (version simplifiée)"""
        if not self.current_receipt:
            messagebox.showwarning("Attention", "Aucun reçu sélectionné")
            return

        # Pour une vraie impression, vous utiliseriez:
        # import win32api  # Windows
        # ou créer un PDF temporaire et l'ouvrir

        # Solution simple: ouvrir avec le visualiseur PDF par défaut
        try:
            # Créer un PDF temporaire
            import tempfile
            temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            temp_pdf.close()

            # Générer le PDF dans le fichier temporaire
            self.current_receipt_temp_path = temp_pdf.name
            old_generate = self.generate_pdf_receipt

            # Rediriger temporairement generate_pdf_receipt
            def temp_generate():
                self.generate_pdf_receipt = old_generate
                # Ouvrir le PDF avec le programme par défaut
                import os
                import platform

                if platform.system() == 'Windows':
                    os.startfile(self.current_receipt_temp_path)
                elif platform.system() == 'Darwin':  # macOS
                    os.system(f'open "{self.current_receipt_temp_path}"')
                else:  # Linux
                    os.system(f'xdg-open "{self.current_receipt_temp_path}"')

                # Nettoyer après 30 secondes
                self.after(30000, lambda: os.unlink(self.current_receipt_temp_path))

            self.generate_pdf_receipt = lambda: self._save_to_temp_and_open(temp_pdf.name)

            # Appeler la version modifiée
            self._save_to_temp_and_open(temp_pdf.name)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'imprimer: {e}")

    def _save_to_temp_and_open(self, temp_path):
        """Version interne pour sauvegarder dans un fichier temporaire"""
        try:
            # Création simplifiée du PDF
            c = canvas.Canvas(temp_path, pagesize=A4)
            width, height = A4

            # Contenu simplifié
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2, height - 100, f"Reçu Vente #{self.current_receipt['vente_id']}")

            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, height - 150, f"Montant: {self.current_receipt['montant']:.2f} €")
            c.drawCentredString(width / 2, height - 180, f"Date: {self.current_receipt['date'].strftime('%d/%m/%Y')}")

            c.drawCentredString(width / 2, height - 250, "Merci pour votre achat !")

            c.save()

            # Ouvrir le fichier
            import os
            import platform

            if platform.system() == 'Windows':
                os.startfile(temp_path)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{temp_path}"')
            else:  # Linux
                os.system(f'xdg-open "{temp_path}"')

        except Exception as e:
            print(f"Erreur création PDF temporaire: {e}")
            messagebox.showerror("Erreur", f"Impossible de créer le PDF: {e}")