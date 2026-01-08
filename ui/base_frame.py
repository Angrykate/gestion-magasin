import tkinter as tk

class BaseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Base Frame").pack()
