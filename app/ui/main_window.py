import tkinter as tk
from tkinter import messagebox, ttk

from app.config import APP_TITLE
from app.database import Database
from app.repositories import ProductRepository, SaleRepository
from app.ui.dashboard_view import DashboardView
from app.ui.pos_view import PosView
from app.ui.products_view import ProductsView
from app.ui.sales_view import SalesView
from app.ui.styles import configure_styles


class KioscoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1180x720")
        self.minsize(980, 620)
        configure_styles(self)

        database = Database()
        self.products = ProductRepository(database)
        self.sales = SaleRepository(database)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_view = DashboardView(self.notebook, self.products)
        self.products_view = ProductsView(self.notebook, self.products, self.refresh_all)
        self.pos_view = PosView(self.notebook, self.products, self.sales, self.refresh_all)
        self.sales_view = SalesView(self.notebook, self.sales)

        self.notebook.add(self.dashboard_view, text="  Dashboard  ")
        self.notebook.add(self.products_view, text="  Productos  ")
        self.notebook.add(self.pos_view, text="  Caja  ")
        self.notebook.add(self.sales_view, text="  Ventas  ")
        self.notebook.bind("<<NotebookTabChanged>>", lambda _event: self.refresh_all())

        menu = tk.Menu(self)
        data_menu = tk.Menu(menu, tearoff=False)
        data_menu.add_command(label="Cargar productos de ejemplo", command=self.load_demo)
        data_menu.add_separator()
        data_menu.add_command(label="Salir", command=self.destroy)
        menu.add_cascade(label="Datos", menu=data_menu)
        self.config(menu=menu)

        self.refresh_all()

    def refresh_all(self) -> None:
        self.dashboard_view.refresh()
        self.products_view.refresh()
        self.pos_view.refresh()
        self.sales_view.refresh()

    def load_demo(self) -> None:
        inserted = self.products.database.seed_demo_products()
        self.refresh_all()
        if inserted:
            messagebox.showinfo("Datos de ejemplo", f"Se agregaron {inserted} productos.", parent=self)
        else:
            messagebox.showinfo("Datos de ejemplo", "Los productos de ejemplo ya existen.", parent=self)

