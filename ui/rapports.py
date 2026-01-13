import tkinter as tk

class RapportsFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Rapport Page").pack()