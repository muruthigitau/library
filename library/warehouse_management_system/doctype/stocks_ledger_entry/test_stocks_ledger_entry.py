# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime

class TestStocksLedgerEntry(FrappeTestCase):

	def setUp(self):
		"""Set up test data."""
		# Clean up existing test data
		self.clean_up_test_data()

		# Create a product and warehouse for the test
		self.product = self.get_or_create_product("Test Product")
		self.warehouse = self.get_or_create_warehouse("Test Warehouse")

		# Create a previous stock entry
		self.create_stock_entry(
			product=self.product,
			warehouse=self.warehouse,
			quantity=50,
			valuation_rate=100,
			stock_value_after_transaction=5000,
			posting_datetime="2024-09-01 10:00:00"
		)

	def tearDown(self):
		"""Clean up after each test."""
		self.clean_up_test_data()

	def test_stock_valuation_on_receipt(self):
		"""Test stock valuation calculation for a receipt transaction."""
		entry = self.create_stock_entry(
			product=self.product,
			warehouse=self.warehouse,
			quantity=30,
			valuation_rate=120,
			posting_datetime="2024-09-02 10:00:00"
		)

		# Check if the moving average cost is calculated correctly
		previous_qty = 50
		previous_rate = 100
		new_qty = 30
		new_rate = 120
		expected_moving_average_cost = self.calculate_moving_average(
			old_qty=previous_qty,
			old_rate=previous_rate,
			new_qty=new_qty,
			new_rate=new_rate
		)
		self.assertAlmostEqual(entry.moving_average_cost, expected_moving_average_cost, places=2)

		# Check if stock values are updated correctly
		expected_stock_value_before = 5000
		expected_stock_value_after = expected_stock_value_before + (30 * 120)
		self.assertEqual(entry.stock_value_before_transaction, expected_stock_value_before)
		self.assertEqual(entry.stock_value_after_transaction, expected_stock_value_after)
		self.assertEqual(entry.total_value, expected_stock_value_after)
		self.assertEqual(entry.stock_value_difference, entry.total_value - entry.stock_value_before_transaction)

	def test_stock_valuation_on_consumption(self):
		"""Test stock valuation calculation for a consumption transaction."""
		
		# Create an entry with an earlier date to simulate a previous stock receipt
		self.create_stock_entry(
			product=self.product,
			warehouse=self.warehouse,
			quantity=30,
			valuation_rate=120,
			posting_datetime="2024-09-03 10:00:00"
		)
		
		# Create another entry for consumption
		entry = self.create_stock_entry(
			product=self.product,
			warehouse=self.warehouse,
			quantity=-20,  # Negative quantity for consumption
			valuation_rate=0,  # Valuation rate should not affect consumption
			posting_datetime="2024-09-04 10:00:00"
		)

		# Fetch the last entry before the current consumption to get the previous moving average cost
		previous_entry = self.get_previous_stock()

		# The moving average cost should remain unchanged for consumption
		self.assertEqual(entry.moving_average_cost, previous_entry['moving_average_cost'])

		# Check if stock values are updated correctly
		expected_stock_value_before = previous_entry['stock_value_after_transaction']
		self.assertEqual(entry.stock_value_before_transaction, expected_stock_value_before)
		self.assertEqual(entry.stock_value_after_transaction, expected_stock_value_before)
		self.assertEqual(entry.total_value, expected_stock_value_before)
		self.assertEqual(entry.stock_value_difference, entry.total_value - entry.stock_value_before_transaction)

	def get_previous_stock(self):
		"""Fetch the stock values and moving average cost from the last transaction before the current one."""
		stock_data = frappe.db.sql("""
			SELECT 
				COALESCE(quantity, 0) AS quantity,
				COALESCE(stock_value_after_transaction, 0) AS stock_value_after_transaction,
				COALESCE(moving_average_cost, 0) AS moving_average_cost
			FROM (
				SELECT 
					quantity,
					stock_value_after_transaction,
					(stock_value_after_transaction / NULLIF(quantity, 0)) AS moving_average_cost
				FROM 
					`tabStocks Ledger Entry`
				WHERE 
					product = %s AND warehouse = %s AND posting_datetime < %s
				ORDER BY 
					posting_datetime DESC
				LIMIT 1
			) AS last_entry
			""", (self.product.name, self.warehouse.name, "2024-09-04 10:00:00"), as_dict=True)
		
		return stock_data[0] if stock_data else {'quantity': 0, 'moving_average_cost': 0, 'stock_value_after_transaction': 0}

	def get_or_create_product(self, product_name):
		"""Get or create a product record."""
		existing_product = frappe.db.get_value("Product", {"name1": product_name})
		if existing_product:
			return frappe.get_doc("Product", existing_product)
		else:
			product = frappe.get_doc({
				"doctype": "Product",
				"name1": product_name,
				"code": 1000,
			})
			product.insert(ignore_permissions=True)
			return product

	def get_or_create_warehouse(self, warehouse_name):
		"""Get or create a warehouse record."""
		existing_warehouse = frappe.db.get_value("Warehouse", {"name1": warehouse_name})
		if existing_warehouse:
			return frappe.get_doc("Warehouse", existing_warehouse)
		else:
			warehouse = frappe.get_doc({
				"doctype": "Warehouse",
				"name1": warehouse_name,
				"code": 1000,
			})
			warehouse.insert(ignore_permissions=True)
			return warehouse

	def create_stock_entry(self, product, warehouse, quantity, valuation_rate, stock_value_after_transaction=None, posting_datetime=now_datetime()):
		"""Create a stock ledger entry record if it does not already exist."""
		
		# Check if a stock entry with the same details already exists
		existing_entry = frappe.db.get_value(
			"Stocks Ledger Entry",
			{
				"product": product.name,
				"warehouse": warehouse.name,
				"quantity": quantity,
				"valuation_rate": valuation_rate,
				"posting_datetime": posting_datetime
			}
		)
		
		if existing_entry:
			# Return the existing entry if it already exists
			return frappe.get_doc("Stocks Ledger Entry", existing_entry)
		
		# Create a new stock entry if it does not exist
		stock_entry = frappe.get_doc({
			"doctype": "Stocks Ledger Entry",
			"product": product.name,
			"warehouse": warehouse.name,
			"quantity": quantity,
			"valuation_rate": valuation_rate,
			"posting_datetime": posting_datetime,
			"stock_value_after_transaction": stock_value_after_transaction or (quantity * valuation_rate),
			"entry_type": "Receipt" if quantity > 0 else "Consume"
		}).insert()
		
		return stock_entry

	def calculate_moving_average(self, old_qty, old_rate, new_qty, new_rate):
		"""Calculate moving average valuation."""
		if old_qty + new_qty == 0:
			return 0
		return ((old_qty * old_rate) + (new_qty * new_rate)) / (old_qty + new_qty)

	def clean_up_test_data(self):
		"""Clean up test data."""
		frappe.db.sql("DELETE FROM `tabProduct` WHERE name LIKE 'Test Product%'")
		frappe.db.sql("DELETE FROM `tabWarehouse` WHERE name LIKE 'Test Warehouse%'")
		frappe.db.sql("DELETE FROM `tabStocks Ledger Entry` WHERE product LIKE 'Test Product%'")
