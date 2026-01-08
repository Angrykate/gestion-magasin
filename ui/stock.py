import tkinter as tk

class StockFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Stock Page").pack()
