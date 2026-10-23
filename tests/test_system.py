import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.database import Database
from app.repositories import ProductRepository, SaleRepository
from app.ui.pos_view import PosView
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

    def test_sale_rejects_invalid_quantities_without_changes(self):
        product_id = self.products.create("C1", "Galletitas", 80000, 5)

        for quantity in (0, -1, 1.5, "2", True):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, "entero mayor que cero"):
                    self.sales.create([{"product_id": product_id, "quantity": quantity}])

        self.assertEqual(self.products.get(product_id)["stock"], 5)
        self.assertEqual(len(self.sales.list_recent()), 0)

    def test_sale_preview_uses_current_price_and_validates_stock(self):
        product_id = self.products.create("D1", "Jugo", 100000, 4)
        cart = [{"product_id": product_id, "quantity": 2, "price_cents": 50000}]
        self.products.update(product_id, "D1", "Jugo", 125000, 4)

        preview = self.sales.preview(cart)

        self.assertEqual(preview[0]["price_cents"], 125000)
        self.assertEqual(preview[0]["subtotal_cents"], 250000)
        self.assertEqual(self.products.get(product_id)["stock"], 4)
        self.assertEqual(len(self.sales.list_recent()), 0)

        self.sales.create(preview)

        sale = self.sales.list_recent()[0]
        self.assertEqual(sale["total_cents"], 250000)
        self.assertEqual(self.products.get(product_id)["stock"], 2)

    def test_pos_confirms_and_registers_sale_with_current_total(self):
        product_id = self.products.create("E1", "Leche", 100000, 4)
        self.products.update(product_id, "E1", "Leche", 125000, 4)
        view = SimpleNamespace(
            cart={
                product_id: {
                    "product_id": product_id,
                    "name": "Leche",
                    "price_cents": 100000,
                    "quantity": 2,
                }
            },
            sales=self.sales,
            on_sale=lambda: None,
            refresh_cart=lambda: None,
        )

        with (
            patch("app.ui.pos_view.messagebox.askyesno", return_value=True) as confirm,
            patch("app.ui.pos_view.messagebox.showinfo") as show_info,
        ):
            PosView.finish_sale(view)

        self.assertIn(format_currency(250000), confirm.call_args.args[1])
        self.assertEqual(self.sales.list_recent()[0]["total_cents"], 250000)
        self.assertEqual(self.products.get(product_id)["stock"], 2)
        self.assertFalse(view.cart)
        show_info.assert_called_once()

    def test_pos_does_not_register_sale_when_confirmation_is_declined(self):
        product_id = self.products.create("F1", "Yogur", 75000, 3)
        view = SimpleNamespace(
            cart={
                product_id: {
                    "product_id": product_id,
                    "name": "Yogur",
                    "price_cents": 75000,
                    "quantity": 1,
                }
            },
            sales=self.sales,
            on_sale=lambda: None,
            refresh_cart=lambda: None,
        )

        with patch("app.ui.pos_view.messagebox.askyesno", return_value=False):
            PosView.finish_sale(view)

        self.assertEqual(self.sales.list_recent(), [])
        self.assertEqual(self.products.get(product_id)["stock"], 3)
        self.assertEqual(view.cart[product_id]["quantity"], 1)

    def test_pos_reports_invalid_cart_without_asking_confirmation(self):
        product_id = self.products.create("G1", "Caramelos", 10000, 3)
        view = SimpleNamespace(
            cart={
                product_id: {
                    "product_id": product_id,
                    "name": "Caramelos",
                    "price_cents": 10000,
                    "quantity": 0,
                }
            },
            sales=self.sales,
            on_sale=lambda: None,
        )

        with (
            patch("app.ui.pos_view.messagebox.showerror") as show_error,
            patch("app.ui.pos_view.messagebox.askyesno") as confirm,
        ):
            PosView.finish_sale(view)

        show_error.assert_called_once()
        confirm.assert_not_called()
        self.assertEqual(self.sales.list_recent(), [])
        self.assertEqual(self.products.get(product_id)["stock"], 3)

    def test_currency_helpers(self):
        self.assertEqual(parse_price_to_cents("1.500,50"), 150050)
        self.assertEqual(parse_price_to_cents("1.500"), 150000)
        self.assertEqual(parse_price_to_cents("1500.50"), 150050)
        self.assertEqual(format_currency(150050), "$ 1.500,50")



if __name__ == "__main__":
    unittest.main()
