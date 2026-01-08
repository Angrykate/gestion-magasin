import tkinter as tk

class CategorieFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Categorie Page").pack()