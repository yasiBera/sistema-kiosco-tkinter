from tkinter import ttk


COLORS = {
    "navy": "#17233C",
    "blue": "#2F6FED",
    "light": "#F4F7FB",
    "white": "#FFFFFF",
    "text": "#172033",
    "muted": "#68758C",
    "green": "#19A974",
    "orange": "#F2994A",
    "red": "#D64545",
}


def configure_styles(root) -> None:
    root.configure(background=COLORS["light"])
    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure("TFrame", background=COLORS["light"])
    style.configure("Card.TFrame", background=COLORS["white"], relief="flat")
    style.configure(
        "Title.TLabel",
        background=COLORS["light"],
        foreground=COLORS["text"],
        font=("Segoe UI", 22, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=COLORS["light"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "CardTitle.TLabel",
        background=COLORS["white"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "CardValue.TLabel",
        background=COLORS["white"],
        foreground=COLORS["text"],
        font=("Segoe UI", 22, "bold"),
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["blue"],
        foreground=COLORS["white"],
        padding=(14, 8),
        font=("Segoe UI", 10, "bold"),
    )
    style.map("Primary.TButton", background=[("active", "#245AC2")])
    style.configure("TButton", padding=(10, 7), font=("Segoe UI", 10))
    style.configure("TEntry", padding=6)
    style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=7)
    style.configure("TNotebook", background=COLORS["light"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        padding=(18, 10),
        font=("Segoe UI", 10, "bold"),
    )

