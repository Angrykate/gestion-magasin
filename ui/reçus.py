import tkinter as tk

class ReçusFrame(tk.Frame):
    def __init__(self, parent,user =None,go_dashboard=None):
        super().__init__(parent)
        tk.Label(self, text="Reçus Page").pack()