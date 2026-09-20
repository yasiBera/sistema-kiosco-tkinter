from typing import Iterable

from app.config import LOW_STOCK_LIMIT
from app.database import Database


class ProductRepository:
    def __init__(self, database: Database):
        self.database = database

    def list_all(self, search: str = "", only_active: bool = False):
        conditions = []
        parameters: list[object] = []
        if search.strip():
            conditions.append("(code LIKE ? OR name LIKE ?)")
            term = f"%{search.strip()}%"
            parameters.extend([term, term])
        if only_active:
            conditions.append("active = 1")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        with self.database.read() as connection:
            return connection.execute(
                f"""
                SELECT id, code, name, price_cents, stock, active
                FROM products {where}
                ORDER BY name COLLATE NOCASE
                """,
                parameters,
            ).fetchall()

    def get(self, product_id: int):
        with self.database.read() as connection:
            return connection.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()

    def create(self, code: str, name: str, price_cents: int, stock: int) -> int:
        with self.database.transaction() as connection:
            cursor = connection.execute(
                """
                INSERT INTO products(code, name, price_cents, stock)
                VALUES (?, ?, ?, ?)
                """,
                (code.strip(), name.strip(), price_cents, stock),
            )
            return int(cursor.lastrowid)

    def update(
        self, product_id: int, code: str, name: str, price_cents: int, stock: int
    ) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                """
                UPDATE products
                SET code = ?, name = ?, price_cents = ?, stock = ?
                WHERE id = ?
                """,
                (code.strip(), name.strip(), price_cents, stock, product_id),
            )

    def set_active(self, product_id: int, active: bool) -> None:
        with self.database.transaction() as connection:
            connection.execute(
                "UPDATE products SET active = ? WHERE id = ?",
                (int(active), product_id),
            )

    def dashboard_stats(self):
        with self.database.read() as connection:
            products = connection.execute(
                "SELECT COUNT(*) FROM products WHERE active = 1"
            ).fetchone()[0]
            low_stock = connection.execute(
                "SELECT COUNT(*) FROM products WHERE active = 1 AND stock <= ?",
                (LOW_STOCK_LIMIT,),
            ).fetchone()[0]
            today = connection.execute(
                """
                SELECT COUNT(*) AS sales_count, COALESCE(SUM(total_cents), 0) AS revenue
                FROM sales WHERE date(created_at) = date('now', 'localtime')
                """
            ).fetchone()
            return {
                "products": products,
                "low_stock": low_stock,
                "sales_today": today["sales_count"],
                "revenue_today": today["revenue"],
            }


class SaleRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, items: Iterable[dict]) -> int:
        normalized = [dict(item) for item in items]
        if not normalized:
            raise ValueError("La venta no tiene productos.")

        with self.database.transaction() as connection:
            total_cents = 0
            checked_items = []
            for item in normalized:
                product = connection.execute(
                    """
                    SELECT id, name, price_cents, stock, active
                    FROM products WHERE id = ?
                    """,
                    (item["product_id"],),
                ).fetchone()
                if product is None or not product["active"]:
                    raise ValueError("Uno de los productos ya no está disponible.")

                quantity = int(item["quantity"])
                if quantity <= 0:
                    raise ValueError("La cantidad debe ser mayor que cero.")
                if product["stock"] < quantity:
                    raise ValueError(
                        f"Stock insuficiente para {product['name']}. "
                        f"Disponible: {product['stock']}."
                    )

                subtotal = product["price_cents"] * quantity
                total_cents += subtotal
                checked_items.append((product, quantity, subtotal))

            cursor = connection.execute(
                "INSERT INTO sales(created_at, total_cents) VALUES (?, ?)",
                (self.database.now_text(), total_cents),
            )
            sale_id = int(cursor.lastrowid)

            for product, quantity, subtotal in checked_items:
                connection.execute(
                    """
                    INSERT INTO sale_items(
                        sale_id, product_id, product_name, quantity,
                        unit_price_cents, subtotal_cents
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        sale_id,
                        product["id"],
                        product["name"],
                        quantity,
                        product["price_cents"],
                        subtotal,
                    ),
                )
                connection.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (quantity, product["id"]),
                )
            return sale_id

    def list_recent(self, limit: int = 100):
        with self.database.read() as connection:
            return connection.execute(
                """
                SELECT s.id, s.created_at, s.total_cents,
                       COALESCE(SUM(si.quantity), 0) AS units
                FROM sales AS s
                LEFT JOIN sale_items AS si ON si.sale_id = s.id
                GROUP BY s.id
                ORDER BY s.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def get_items(self, sale_id: int):
        with self.database.read() as connection:
            return connection.execute(
                """
                SELECT product_name, quantity, unit_price_cents, subtotal_cents
                FROM sale_items WHERE sale_id = ? ORDER BY id
                """,
                (sale_id,),
            ).fetchall()
