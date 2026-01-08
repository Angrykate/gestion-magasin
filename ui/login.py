import tkinter as tk

class LoginFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Login Page").pack()
