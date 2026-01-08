import tkinter as tk

class ProduitsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Produits Page").pack()
