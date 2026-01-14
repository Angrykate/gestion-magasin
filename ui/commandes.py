import tkinter as tk

class CommandeAchatFrame(tk.Frame):
    def __init__(self, parent,user =None,go_dashboard=None):
        super().__init__(parent)
        tk.Label(self, text="Commande Achat Page").pack()
