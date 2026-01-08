import tkinter as tk

class VentesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Ventes Page").pack()
