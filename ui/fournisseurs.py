import tkinter as tk

class FournisseurFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Fournisseur Page").pack()