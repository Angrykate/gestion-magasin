import tkinter as tk
from ui.base_frame import BaseFrame
from ui.dashboard import DashboardFrame

root = tk.Tk()
root.title("Gestion de magasin")
root.geometry("1270x668")
root.resizable(False, False)

base = BaseFrame(root, user_name="Jean Dupont", user_role="Administrateur")
DashboardFrame(base.content_frame)

root.mainloop()
