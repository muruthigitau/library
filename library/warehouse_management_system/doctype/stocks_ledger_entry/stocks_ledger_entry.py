# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class StocksLedgerEntry(Document):
    def before_save(self):
        """Before saving the stock ledger entry, calculate the moving average valuation."""
        self.update_stock_valuation()

    def update_stock_valuation(self):
        """Calculate moving average valuation and update stock values."""
        previous_stock = self.get_previous_stock()
        
        # Calculate the new moving average cost
        if self.quantity > 0 and self.entry_type == 'Receipt':  # For incoming stock (receipt)
            new_moving_average_cost = self.calculate_moving_average(
                previous_stock['quantity'], previous_stock['moving_average_cost'],
                self.quantity, self.valuation_rate
            )
            self.moving_average_cost = new_moving_average_cost
        else:
            # For consumption or transfer - moving_average_cost remains unchanged
            self.moving_average_cost = previous_stock['moving_average_cost']

        # Update stock values
        self.stock_value_before_transaction = flt(previous_stock['stock_value_after_transaction'])
        self.stock_value_after_transaction = self.stock_value_before_transaction + (flt(self.quantity) * flt(self.valuation_rate))
        self.total_value = self.stock_value_after_transaction
        self.stock_value_difference = self.total_value - self.stock_value_before_transaction

    def get_previous_stock(self):
        """Fetch the stock values and moving average cost from the last transaction."""
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
            """, (self.product, self.warehouse, self.posting_datetime), as_dict=True)

        return stock_data[0] if stock_data else {'quantity': 0, 'moving_average_cost': 0, 'stock_value_after_transaction': 0}

    def calculate_moving_average(self, old_qty, old_rate, new_qty, new_rate):
        """Calculate moving average valuation."""
        if old_qty + new_qty == 0:
            return 0
        return ((old_qty * old_rate) + (new_qty * new_rate)) / (old_qty + new_qty)
