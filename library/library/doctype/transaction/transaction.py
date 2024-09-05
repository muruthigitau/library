# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate, add_days, getdate
import ast
from frappe.model.document import Document

class Transaction(Document):
    def before_save(self):
        settings = frappe.get_doc("My Settings", "My Settings")
        max_lease_days = settings.max_lease_days if settings.max_lease_days else 0
        if self.date:
            self.due_date = add_days(self.date, max_lease_days)
        if self.is_new():
            for book_entry in self.book_list:
                book = frappe.get_doc("Book", book_entry.book)
                book.available_copies = max(book.available_copies - book_entry.copies, 0) 
                book.save() 

@frappe.whitelist()
def calculate_fees(transaction_name):
    transaction = frappe.get_doc("Transaction", transaction_name)   
    rent_fee_incurred = 0
    late_fee_incurred = 0
    today = getdate(nowdate())
    due_date = getdate(transaction.due_date) if transaction.due_date else None   
    for book_entry in transaction.book_list:
        book = frappe.get_doc("Book", book_entry.book)       
        if transaction.date and due_date:
            rent_fee_per_day = book.rent_fee_per_day * book_entry.copies 
            rent_days = min((due_date - getdate(transaction.date)).days, (today - getdate(transaction.date)).days)
            rent_fee_incurred += rent_days * rent_fee_per_day       
        if due_date and today > due_date:
            late_fee_rate = book.late_fee_rate * book_entry.copies
            late_days = (today - due_date).days
            late_fee_incurred += late_days * late_fee_rate   
    total_fee = rent_fee_incurred + late_fee_incurred
    return {
        "rent_fee_incurred": rent_fee_incurred,
        "late_fee_incurred": late_fee_incurred,
        "total_fee": total_fee
    }

@frappe.whitelist()
def get_total_payments(payments):
    """
    This method calculates the total payments based on a list of linked payment documents.
    Args:
        payments (list): A list of linked Payment documents (names).
    Returns:
        dict: A dictionary with the total payments amount.
    """
    payments = ast.literal_eval(payments)
    if not payments:
        return {"total_payments": 0.0}

    total_amount = 0
    for p in list(payments):
        payment = frappe.get_doc("Payment", p)
        total_amount += payment.amount

    return {"total_payments": total_amount}
