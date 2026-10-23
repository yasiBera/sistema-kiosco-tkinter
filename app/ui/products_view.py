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

        self.search_var = tk.StringVar()
        toolbar = ttk.Frame(self, padding=12)
        toolbar.pack(fill="x", pady=(0, 8))
        toolbar.columnconfigure(1, weight=1)
        ttk.Label(toolbar, text="Buscar productos", style="Field.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(toolbar, text="Filtrá por nombre o código", foreground="#68758C").grid(
            row=1, column=0, sticky="w", pady=(2, 0)
        )
        search = ttk.Entry(toolbar, textvariable=self.search_var)
        search.grid(row=0, column=1, rowspan=2, sticky="ew", padx=12)
        search.bind("<KeyRelease>", lambda _event: self.refresh())
        ttk.Button(
            toolbar, text="Nuevo producto", style="Primary.TButton",
            command=self.open_form,
        ).grid(row=0, column=2, rowspan=2, sticky="e")

        list_header = ttk.Frame(self)
        list_header.pack(fill="x", pady=(4, 8))
        ttk.Label(list_header, text="Listado de productos", style="Section.TLabel").pack(
            side="left"
        )
        ttk.Label(
            list_header, text="Doble clic para editar", foreground="#68758C"
        ).pack(side="right")

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
        table_area = ttk.Frame(self)
        table_area.pack(fill="both", expand=True)
        table_area.columnconfigure(0, weight=1)
        table_area.rowconfigure(0, weight=1)
        self.tree.grid(in_=table_area, row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_area, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", lambda _event: self.edit_selected())

        actions = ttk.Frame(self)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Editar producto", command=self.edit_selected).pack(side="left")
        ttk.Button(
            actions, text="Cambiar estado", command=self.toggle_selected
        ).pack(side="left", padx=8)
        self.empty_label = ttk.Label(actions, foreground="#68758C")
        self.empty_label.pack(side="right")

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        products = self.products.list_all(self.search_var.get())
        for product in products:
            self.tree.insert(
                "", "end", iid=str(product["id"]),
                values=(
                    product["code"], product["name"],
                    format_currency(product["price_cents"]), product["stock"],
                    "Activo" if product["active"] else "Inactivo",
                ),
            )
        if products:
            self.empty_label.configure(text=f"{len(products)} productos")
        elif self.search_var.get().strip():
            self.empty_label.configure(text="No hay coincidencias para esa búsqueda.")
        else:
            self.empty_label.configure(text="Todavía no hay productos cargados.")

    def selected_product_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Productos", "Seleccioná un producto del listado para continuar.", parent=self
            )
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

