import tempfile
import unittest
from pathlib import Path

from app.database import Database
from app.repositories import ProductRepository, SaleRepository
from app.utils import (
    calculate_price_with_markup,
    format_currency,
    parse_markup_percent,
    parse_price_to_cents,
)


class KioscoSystemTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = Database(Path(self.temp_dir.name) / "test.db")
        self.products = ProductRepository(database)
        self.sales = SaleRepository(database)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_product_and_sale_updates_stock(self):
        product_id = self.products.create("A1", "Alfajor", 100000, 0, 5)
        sale_id = self.sales.create([{"product_id": product_id, "quantity": 2}])

        self.assertGreater(sale_id, 0)
        self.assertEqual(self.products.get(product_id)["stock"], 3)
        sale = self.sales.list_recent()[0]
        self.assertEqual(sale["total_cents"], 200000)
        self.assertEqual(sale["units"], 2)

    def test_product_codes_are_case_insensitive_and_normalized(self):
        product_id = self.products.create(" ab12 ", "Alfajor", 100000, 0, 5)
        self.assertEqual(self.products.get(product_id)["code"], "AB12")

        with self.assertRaisesRegex(ValueError, "sin distinguir mayúsculas"):
            self.products.create("ab12", "Otro alfajor", 120000, 0, 3)

    def test_product_update_rejects_another_products_code(self):
        first_id = self.products.create("A1", "Agua", 100000, 0, 5)
        second_id = self.products.create("B1", "Gaseosa", 150000, 0, 4)

        with self.assertRaisesRegex(ValueError, "sin distinguir mayúsculas"):
            self.products.update(second_id, "a1", "Gaseosa", 150000, 0, 4)

        self.assertEqual(self.products.get(second_id)["code"], "B1")
        self.products.update(first_id, "a1", "Agua", 100000, 0, 5)
        self.assertEqual(self.products.get(first_id)["code"], "A1")

    def test_sale_rejects_insufficient_stock_without_changes(self):
        product_id = self.products.create("B1", "Gaseosa", 150000, 0, 1)

        with self.assertRaisesRegex(ValueError, "Stock insuficiente"):
            self.sales.create([{"product_id": product_id, "quantity": 2}])

        self.assertEqual(self.products.get(product_id)["stock"], 1)
        self.assertEqual(len(self.sales.list_recent()), 0)

    def test_cost_markup_calculates_sale_price_and_profit(self):
        sale_price, profit = calculate_price_with_markup(80000, 30)
        self.assertEqual(sale_price, 104000)
        self.assertEqual(profit, 24000)
        product_id = self.products.create("M1", "Producto con margen", 80000, 30, 5)
        product = self.products.get(product_id)
        self.assertEqual(product["price_cents"], 104000)
        self.assertEqual(product["cost_cents"], 80000)
        self.assertEqual(product["markup_percent"], 30)

    def test_markup_requires_a_non_negative_integer(self):
        self.assertEqual(parse_markup_percent("25"), 25)
        for value in ("", "25.5", "abc", "-5"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_markup_percent(value)

    def test_currency_helpers(self):
        self.assertEqual(parse_price_to_cents("1.500,50"), 150050)
        self.assertEqual(parse_price_to_cents("1.500"), 150000)
        self.assertEqual(parse_price_to_cents("1500.50"), 150050)
        self.assertEqual(format_currency(150050), "$ 1.500,50")

    def test_price_rejects_non_finite_numbers(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "número finito"):
                    parse_price_to_cents(value)



if __name__ == "__main__":
    unittest.main()
