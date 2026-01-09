import tkinter as tk
from ui.login import LoginFrame
from ui.base_frame import BaseFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Système de gestion de magasin")
        self.geometry("1270x668+0+0")
        self.resizable(False, False)

        self.current_user = None

        self.show_login()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        LoginFrame(self, on_login_success=self.show_base).pack(fill=tk.BOTH, expand=True)

    def show_base(self, user):
        self.current_user = user
        self.clear()
        BaseFrame(self, user=user, on_logout=self.show_login).pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
