import tkinter as tk

class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Dashboard Page").pack()