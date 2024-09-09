# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    """Return columns and data for the Stock Balance report."""
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    """Return columns for the Stock Balance report."""
    return [
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
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
            "label": _("Total Quantity"),
            "fieldname": "total_quantity",
            "fieldtype": "Int",
        },
        {
            "label": _("Total Value"),
            "fieldname": "total_value",
            "fieldtype": "Currency",
        },
        {
            "label": _("Moving Average Cost"),
            "fieldname": "moving_average_cost",
            "fieldtype": "Currency",
        },
    ]

def get_data(filters):
    """Return data for the Stock Balance report."""
    conditions = []
    values = []

    if filters.get("product"):
        conditions.append("product = %s")
        values.append(filters["product"])
    if filters.get("warehouse"):
        conditions.append("warehouse = %s")
        values.append(filters["warehouse"])

    # Handle date filter
    as_of_date = filters.get("posting_datetime")
    if as_of_date:
        conditions.append("DATE(posting_datetime) = %s")
        values.append(as_of_date)

    # Build the condition string
    condition_str = " AND ".join(conditions) if conditions else "1=1"
    
    # Query to get stock balance aggregated by date
    query = f"""
    SELECT 
        DATE(posting_datetime) AS posting_date,
        product,
        warehouse,
        SUM(quantity) AS total_quantity,
        SUM(stock_value_after_transaction) AS total_value,
        (SUM(stock_value_after_transaction) / NULLIF(SUM(quantity), 0)) AS moving_average_cost
    FROM 
        `tabStocks Ledger Entry`
    WHERE 
        {condition_str}
    GROUP BY 
        DATE(posting_datetime), product, warehouse
    ORDER BY 
        DATE(posting_datetime), product, warehouse;
    """
    
    # Return aggregated data by date
    return frappe.db.sql(query, values, as_dict=True)
