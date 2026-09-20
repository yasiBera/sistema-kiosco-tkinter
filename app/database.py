import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from app.config import DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    total_cents INTEGER NOT NULL CHECK(total_cents >= 0)
);

CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
    subtotal_cents INTEGER NOT NULL CHECK(subtotal_cents >= 0),
    FOREIGN KEY(sale_id) REFERENCES sales(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
"""


class Database:
    def __init__(self, path: Path | str = DATABASE_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @contextmanager
    def read(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(SCHEMA)

    def seed_demo_products(self) -> int:
        demo = [
            ("779001", "Agua mineral 500 ml", 100000, 12),
            ("779002", "Gaseosa cola 500 ml", 180000, 10),
            ("779003", "Alfajor de chocolate", 90000, 20),
            ("779004", "Papas fritas", 150000, 8),
            ("779005", "Caramelos", 15000, 40),
        ]
        with self.transaction() as connection:
            before = connection.total_changes
            connection.executemany(
                """
                INSERT OR IGNORE INTO products(code, name, price_cents, stock)
                VALUES (?, ?, ?, ?)
                """,
                demo,
            )
            return connection.total_changes - before

    @staticmethod
    def now_text() -> str:
        return datetime.now().isoformat(timespec="seconds")
