import tkinter as tk

class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#e9ecef')
        self.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            self,
            text="Dashboard",
            font=('times new roman', 18, 'bold'),
            bg='#e9ecef'
        ).pack(padx=20, pady=20)
