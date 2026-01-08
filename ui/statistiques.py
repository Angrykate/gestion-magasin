import tkinter as tk

class StatistiquesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Statistiques Page").pack()
