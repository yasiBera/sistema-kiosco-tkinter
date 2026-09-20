import tkinter as tk
from tkinter import messagebox, ttk

from app.repositories import ProductRepository, SaleRepository
from app.ui.styles import COLORS
from app.utils import format_currency


class PosView(ttk.Frame):
    def __init__(
        self,
        parent,
        products: ProductRepository,
        sales: SaleRepository,
        on_sale,
    ):
        super().__init__(parent, padding=24)
        self.products = products
        self.sales = sales
        self.on_sale = on_sale
        self.cart: dict[int, dict] = {}

        ttk.Label(self, text="Caja", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Seleccioná productos, armá el carrito y confirmá la venta",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(1, weight=1)

        self.search_var = tk.StringVar()
        search_area = ttk.Frame(content)
        search_area.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=(0, 8))
        ttk.Label(search_area, text="Buscar por nombre o código:").pack(side="left")
        search = ttk.Entry(search_area, textvariable=self.search_var)
        search.pack(side="left", fill="x", expand=True, padx=8)
        search.bind("<KeyRelease>", lambda _event: self.refresh_products())

        self.product_tree = ttk.Treeview(
            content, columns=("name", "price", "stock"), show="headings", selectmode="browse"
        )
        self.product_tree.heading("name", text="Producto")
        self.product_tree.heading("price", text="Precio")
        self.product_tree.heading("stock", text="Stock")
        self.product_tree.column("name", width=300)
        self.product_tree.column("price", width=110, anchor="center")
        self.product_tree.column("stock", width=70, anchor="center")
        self.product_tree.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self.product_tree.bind("<Double-1>", lambda _event: self.add_selected())
        ttk.Button(content, text="Agregar al carrito", style="Primary.TButton",
                   command=self.add_selected).grid(row=2, column=0, sticky="e", padx=(0, 12), pady=10)

        cart_panel = tk.Frame(content, bg=COLORS["white"], highlightthickness=1,
                              highlightbackground="#E4E9F1")
        cart_panel.grid(row=0, column=1, rowspan=3, sticky="nsew")
        cart_panel.rowconfigure(1, weight=1)
        cart_panel.columnconfigure(0, weight=1)
        tk.Label(cart_panel, text="Venta actual", bg=COLORS["white"], fg=COLORS["text"],
                 font=("Segoe UI", 15, "bold")).grid(row=0, column=0, sticky="w", padx=16, pady=14)

        self.cart_tree = ttk.Treeview(
            cart_panel, columns=("name", "qty", "subtotal"), show="headings", selectmode="browse"
        )
        self.cart_tree.heading("name", text="Producto")
        self.cart_tree.heading("qty", text="Cant.")
        self.cart_tree.heading("subtotal", text="Subtotal")
        self.cart_tree.column("name", width=190)
        self.cart_tree.column("qty", width=55, anchor="center")
        self.cart_tree.column("subtotal", width=100, anchor="e")
        self.cart_tree.grid(row=1, column=0, sticky="nsew", padx=12)

        cart_actions = ttk.Frame(cart_panel)
        cart_actions.grid(row=2, column=0, sticky="ew", padx=12, pady=8)
        ttk.Button(cart_actions, text="− 1", command=self.decrease_selected).pack(side="left")
        ttk.Button(cart_actions, text="Vaciar", command=self.clear_cart).pack(side="right")

        self.total_label = tk.Label(cart_panel, text="TOTAL  $ 0,00", bg=COLORS["navy"],
                                    fg=COLORS["white"], font=("Segoe UI", 18, "bold"), pady=14)
        self.total_label.grid(row=3, column=0, sticky="ew")
        ttk.Button(cart_panel, text="CONFIRMAR VENTA", style="Primary.TButton",
                   command=self.finish_sale).grid(row=4, column=0, sticky="ew", padx=12, pady=12)

    def refresh(self) -> None:
        self.refresh_products()
        self.refresh_cart()

    def refresh_products(self) -> None:
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
        for product in self.products.list_all(self.search_var.get(), only_active=True):
            self.product_tree.insert(
                "", "end", iid=str(product["id"]),
                values=(product["name"], format_currency(product["price_cents"]), product["stock"]),
            )

    def add_selected(self) -> None:
        selected = self.product_tree.selection()
        if not selected:
            messagebox.showwarning("Caja", "Seleccioná un producto.", parent=self)
            return
        product_id = int(selected[0])
        product = self.products.get(product_id)
        current_quantity = self.cart.get(product_id, {}).get("quantity", 0)
        if current_quantity >= product["stock"]:
            messagebox.showwarning("Caja", "No hay más unidades disponibles.", parent=self)
            return
        self.cart[product_id] = {
            "product_id": product_id,
            "name": product["name"],
            "price_cents": product["price_cents"],
            "quantity": current_quantity + 1,
        }
        self.refresh_cart()

    def decrease_selected(self) -> None:
        selected = self.cart_tree.selection()
        if not selected:
            return
        product_id = int(selected[0])
        self.cart[product_id]["quantity"] -= 1
        if self.cart[product_id]["quantity"] <= 0:
            del self.cart[product_id]
        self.refresh_cart()

    def clear_cart(self) -> None:
        self.cart.clear()
        self.refresh_cart()

    def refresh_cart(self) -> None:
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        total = 0
        for product_id, item in self.cart.items():
            subtotal = item["price_cents"] * item["quantity"]
            total += subtotal
            self.cart_tree.insert(
                "", "end", iid=str(product_id),
                values=(item["name"], item["quantity"], format_currency(subtotal)),
            )
        self.total_label.configure(text=f"TOTAL  {format_currency(total)}")

    def finish_sale(self) -> None:
        if not self.cart:
            messagebox.showwarning("Caja", "Agregá al menos un producto.", parent=self)
            return
        total = sum(item["price_cents"] * item["quantity"] for item in self.cart.values())
        if not messagebox.askyesno(
            "Confirmar venta", f"¿Registrar la venta por {format_currency(total)}?", parent=self
        ):
            return
        try:
            sale_id = self.sales.create(self.cart.values())
        except ValueError as exc:
            messagebox.showerror("No se pudo vender", str(exc), parent=self)
            self.on_sale()
            return
        self.cart.clear()
        self.on_sale()
        messagebox.showinfo("Venta registrada", f"Venta N.º {sale_id} guardada correctamente.", parent=self)

