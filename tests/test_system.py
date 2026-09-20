import tempfile
import unittest
from pathlib import Path

from app.database import Database
from app.repositories import ProductRepository, SaleRepository
from app.utils import format_currency, parse_price_to_cents


class KioscoSystemTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = Database(Path(self.temp_dir.name) / "test.db")
        self.products = ProductRepository(database)
        self.sales = SaleRepository(database)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_product_and_sale_updates_stock(self):
        product_id = self.products.create("A1", "Alfajor", 100000, 5)
        sale_id = self.sales.create([{"product_id": product_id, "quantity": 2}])

        self.assertGreater(sale_id, 0)
        self.assertEqual(self.products.get(product_id)["stock"], 3)
        sale = self.sales.list_recent()[0]
        self.assertEqual(sale["total_cents"], 200000)
        self.assertEqual(sale["units"], 2)

    def test_sale_rejects_insufficient_stock_without_changes(self):
        product_id = self.products.create("B1", "Gaseosa", 150000, 1)

        with self.assertRaisesRegex(ValueError, "Stock insuficiente"):
            self.sales.create([{"product_id": product_id, "quantity": 2}])

        self.assertEqual(self.products.get(product_id)["stock"], 1)
        self.assertEqual(len(self.sales.list_recent()), 0)

    def test_currency_helpers(self):
        self.assertEqual(parse_price_to_cents("1.500,50"), 150050)
        self.assertEqual(parse_price_to_cents("1.500"), 150000)
        self.assertEqual(parse_price_to_cents("1500.50"), 150050)
        self.assertEqual(format_currency(150050), "$ 1.500,50")



if __name__ == "__main__":
    unittest.main()
