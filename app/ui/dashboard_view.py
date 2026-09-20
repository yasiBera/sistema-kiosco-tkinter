import tkinter as tk
from tkinter import ttk

from app.repositories import ProductRepository
from app.ui.styles import COLORS
from app.utils import format_currency


class DashboardView(ttk.Frame):
    def __init__(self, parent, products: ProductRepository):
        super().__init__(parent, padding=24)
        self.products = products
        self.values: dict[str, ttk.Label] = {}

        ttk.Label(self, text="Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self,
            text="Resumen general del kiosco",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 20))

        cards = ttk.Frame(self)
        cards.pack(fill="x")
        for column in range(4):
            cards.columnconfigure(column, weight=1, uniform="cards")

        data = [
            ("products", "PRODUCTOS ACTIVOS", COLORS["blue"]),
            ("low_stock", "STOCK BAJO", COLORS["orange"]),
            ("sales_today", "VENTAS DE HOY", COLORS["green"]),
            ("revenue_today", "RECAUDACIÓN DE HOY", COLORS["navy"]),
        ]
        for index, (key, title, color) in enumerate(data):
            card = tk.Frame(cards, bg=COLORS["white"], highlightthickness=1,
                            highlightbackground="#E4E9F1")
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 7, 7))
            tk.Frame(card, bg=color, height=5).pack(fill="x")
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(
                anchor="w", padx=18, pady=(18, 5)
            )
            label = ttk.Label(card, text="0", style="CardValue.TLabel")
            label.pack(anchor="w", padx=18, pady=(0, 20))
            self.values[key] = label

        note = tk.Frame(self, bg=COLORS["white"], highlightthickness=1,
                        highlightbackground="#E4E9F1")
        note.pack(fill="x", pady=24)
        tk.Label(
            note,
            text="Proyecto educativo",
            bg=COLORS["white"],
            fg=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=20, pady=(18, 5))
        tk.Label(
            note,
            text=(
                "Esta versión inicial permite administrar productos y registrar ventas. "
                "Cada venta descuenta el stock automáticamente."
            ),
            bg=COLORS["white"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            wraplength=800,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 18))

    def refresh(self) -> None:
        stats = self.products.dashboard_stats()
        self.values["products"].configure(text=str(stats["products"]))
        self.values["low_stock"].configure(text=str(stats["low_stock"]))
        self.values["sales_today"].configure(text=str(stats["sales_today"]))
        self.values["revenue_today"].configure(
            text=format_currency(stats["revenue_today"])
        )

