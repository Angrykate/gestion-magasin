import tkinter as tk
from ui.login import LoginFrame

root = tk.Tk()
root.title("Système de gestion de magasin")

login_page = LoginFrame(root)
login_page.pack(expand=True, fill="both")

root.mainloop()
