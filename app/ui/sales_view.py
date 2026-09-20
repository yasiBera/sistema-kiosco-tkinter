import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from app.repositories import SaleRepository
from app.utils import format_currency


class SalesView(ttk.Frame):
    def __init__(self, parent, sales: SaleRepository):
        super().__init__(parent, padding=24)
        self.sales = sales

        ttk.Label(self, text="Historial de ventas", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self, text="Últimas 100 operaciones registradas", style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(2, 16))

        columns = ("id", "date", "units", "total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for column, title, width in [
            ("id", "Venta", 80), ("date", "Fecha y hora", 220),
            ("units", "Unidades", 100), ("total", "Total", 150)
        ]:
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _event: self.show_detail())

        ttk.Button(self, text="Ver detalle", command=self.show_detail).pack(anchor="e", pady=(12, 0))

    def refresh(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for sale in self.sales.list_recent():
            date = datetime.fromisoformat(sale["created_at"]).strftime("%d/%m/%Y %H:%M")
            self.tree.insert(
                "", "end", iid=str(sale["id"]),
                values=(f"#{sale['id']}", date, sale["units"], format_currency(sale["total_cents"])),
            )

    def show_detail(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ventas", "Seleccioná una venta.", parent=self)
            return
        sale_id = int(selected[0])
        lines = []
        for item in self.sales.get_items(sale_id):
            lines.append(
                f"{item['quantity']} × {item['product_name']}  —  "
                f"{format_currency(item['subtotal_cents'])}"
            )
        messagebox.showinfo(f"Detalle de venta #{sale_id}", "\n".join(lines), parent=self)

