# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """Return columns and data for the Stocks Ledger report."""
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Return columns for the Stocks Ledger report."""
    return [
        {
            "label": _("Posting Date"),
            "fieldname": "posting_datetime",
            "fieldtype": "Datetime",
        },
        {
            "label": _("Product"),
            "fieldname": "product",
            "fieldtype": "Link",
            "options": "Product",
        },
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
        },
        {
            "label": _("Quantity"),
            "fieldname": "quantity",
            "fieldtype": "Int",
        },
        {
            "label": _("Valuation Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
        },
        {
            "label": _("Stock Value Before Transaction"),
            "fieldname": "stock_value_before_transaction",
            "fieldtype": "Currency",
        },
        {
            "label": _("Moving Average Cost"),
            "fieldname": "moving_average_cost",
            "fieldtype": "Currency",
        },
        {
            "label": _("Stock Value After Transaction"),
            "fieldname": "stock_value_after_transaction",
            "fieldtype": "Currency",
        },
        {
            "label": _("Total Value"),
            "fieldname": "total_value",
            "fieldtype": "Currency",
        },
        {
            "label": _("Entry Type"),
            "fieldname": "entry_type",
            "fieldtype": "Select",
            "options": "Receipt\nConsume\nTransfer",
        },
    ]

def get_data(filters):
    """Return data for the Stocks Ledger report."""
    conditions = []
    values = []
    
    if filters.get("product"):
        conditions.append("product = %s")
        values.append(filters["product"])
    if filters.get("warehouse"):
        conditions.append("warehouse = %s")
        values.append(filters["warehouse"])
    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("posting_datetime BETWEEN %s AND %s")
        values.extend([filters["from_date"], filters["to_date"]])
    
    condition_str = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT 
        posting_datetime,
        product,
        warehouse,
        quantity,
        valuation_rate,
        stock_value_before_transaction,
        moving_average_cost,
        stock_value_after_transaction,
        total_value,
        entry_type
    FROM 
        `tabStocks Ledger Entry`
    WHERE 
        {condition_str}
    ORDER BY 
        posting_datetime;
    """
    
    return frappe.db.sql(query, values, as_dict=True)
