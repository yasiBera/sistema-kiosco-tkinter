import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

from app.repositories import ProductRepository
from app.utils import format_currency, parse_price_to_cents


class ProductsView(ttk.Frame):
    def __init__(self, parent, products: ProductRepository, on_change):
        super().__init__(parent, padding=24)
        self.products = products
        self.on_change = on_change
        self.selected_id: int | None = None

        ttk.Label(self, text="Administrar productos", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Alta, modificación de precios y control de stock",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Label(toolbar, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        search = ttk.Entry(toolbar, textvariable=self.search_var, width=35)
        search.pack(side="left", padx=8)
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        ttk.Button(toolbar, text="Nuevo producto", style="Primary.TButton",
                   command=self.open_form).pack(side="right")

        columns = ("code", "name", "price", "stock", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        headings = {
            "code": "Código", "name": "Producto", "price": "Precio",
            "stock": "Stock", "status": "Estado"
        }
        widths = {"code": 120, "name": 360, "price": 130, "stock": 90, "status": 100}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center" if column != "name" else "w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _event: self.edit_selected())

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(actions, text="Editar seleccionado", command=self.edit_selected).pack(side="left")
        ttk.Button(actions, text="Activar / desactivar", command=self.toggle_selected).pack(side="left", padx=8)

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in self.products.list_all(self.search_var.get()):
            self.tree.insert(
                "", "end", iid=str(product["id"]),
                values=(
                    product["code"], product["name"],
                    format_currency(product["price_cents"]), product["stock"],
                    "Activo" if product["active"] else "Inactivo",
                ),
            )

    def selected_product_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Productos", "Seleccioná un producto.", parent=self)
            return None
        return int(selected[0])

    def edit_selected(self) -> None:
        product_id = self.selected_product_id()
        if product_id is not None:
            self.open_form(product_id)

    def toggle_selected(self) -> None:
        product_id = self.selected_product_id()
        if product_id is None:
            return
        product = self.products.get(product_id)
        self.products.set_active(product_id, not bool(product["active"]))
        self.on_change()

    def open_form(self, product_id: int | None = None) -> None:
        product = self.products.get(product_id) if product_id else None
        window = tk.Toplevel(self)
        window.title("Editar producto" if product else "Nuevo producto")
        window.resizable(False, False)
        window.transient(self.winfo_toplevel())
        window.grab_set()

        body = ttk.Frame(window, padding=22)
        body.pack(fill="both", expand=True)
        values = {
            "code": tk.StringVar(value=product["code"] if product else ""),
            "name": tk.StringVar(value=product["name"] if product else ""),
            "price": tk.StringVar(
                value=(f"{product['price_cents'] / 100:.2f}" if product else "")
            ),
            "stock": tk.StringVar(value=str(product["stock"]) if product else "0"),
        }
        fields = [("Código", "code"), ("Nombre", "name"), ("Precio", "price"), ("Stock", "stock")]
        first_entry = None
        for row, (label, key) in enumerate(fields):
            ttk.Label(body, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(body, textvariable=values[key], width=34)
            entry.grid(row=row, column=1, padx=(14, 0), pady=6)
            if first_entry is None:
                first_entry = entry

        def save() -> None:
            try:
                code = values["code"].get().strip()
                name = values["name"].get().strip()
                if not code or not name:
                    raise ValueError("El código y el nombre son obligatorios.")
                price_cents = parse_price_to_cents(values["price"].get())
                stock = int(values["stock"].get())
                if stock < 0:
                    raise ValueError("El stock no puede ser negativo.")
                if product_id:
                    self.products.update(product_id, code, name, price_cents, stock)
                else:
                    self.products.create(code, name, price_cents, stock)
            except ValueError as exc:
                messagebox.showerror("Datos incorrectos", str(exc), parent=window)
                return
            except sqlite3.IntegrityError:
                messagebox.showerror("Código repetido", "Ya existe un producto con ese código.", parent=window)
                return
            window.destroy()
            self.on_change()

        buttons = ttk.Frame(body)
        buttons.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text="Cancelar", command=window.destroy).pack(side="left", padx=6)
        ttk.Button(buttons, text="Guardar", style="Primary.TButton", command=save).pack(side="left")
        window.bind("<Return>", lambda _event: save())
        window.bind("<Escape>", lambda _event: window.destroy())
        first_entry.focus_set()

