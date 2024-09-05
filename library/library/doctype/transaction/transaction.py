# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime, add_days, getdate
import ast
from frappe.model.document import Document

class Transaction(Document):
    def before_save(self):
        settings = frappe.get_doc("My Settings", "My Settings")
        max_lease_days = settings.max_lease_days if settings.max_lease_days else 0
        if self.date:
            self.due_date = add_days(self.date, max_lease_days)
        if self.is_new():
            self.paid=0
            for book_entry in self.book_list:
                book_entry.date_borrowed = now_datetime() 
                book = frappe.get_doc("Book", book_entry.book)
                book.available_copies = max(book.available_copies - book_entry.copies, 0) 
                book.save() 
            if self.member:
                member = frappe.get_doc("Member", self.member)
                for book_entry in self.book_list:
                    new_entry = member.append("borrowing_history", {})
                    new_entry.book = book_entry.get("book")
                    new_entry.copies = book_entry.get("copies") 
                    new_entry.return_date = book_entry.get("return_date") 
                    new_entry.date_borrowed = now_datetime() 
                    new_entry.status = book_entry.get("status")

                member.save()

@frappe.whitelist()
def calculate_fees(transaction_name):
    transaction = frappe.get_doc("Transaction", transaction_name)   
    rent_fee_incurred = 0
    late_fee_incurred = 0
    today = getdate(now_datetime())
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
    transaction.rent_fee_incurred= rent_fee_incurred,
    transaction.late_fee_incurred= late_fee_incurred,
    transaction.total_fee= total_fee
    transaction.save()
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


@frappe.whitelist()
def return_books(transaction_name):
    """
    This method updates the status of all entries in the book_list to 'Returned'
    and updates the corresponding borrowing_history in the Member document.
    
    Args:
        transaction_name (str): The name of the transaction.
    
    Returns:
        dict: A success message.
    """
    # Get the Transaction document
    transaction = frappe.get_doc("Transaction", transaction_name)
    
    if not transaction:
        frappe.throw(("Transaction not found"))

    # Update book_list status to 'Returned'
    for book_entry in transaction.book_list:
        book_entry.status = 'Returned'
        book_entry.return_date = now_datetime() 
    
    # Update borrowing_history in the Member document
    if transaction.member:
        member = frappe.get_doc("Member", transaction.member)
        for book_entry in transaction.book_list:
            # Find the corresponding borrowing_history entry
            for history_entry in member.borrowing_history:
                if history_entry.book == book_entry.book and history_entry.date_borrowed == book_entry.date_borrowed:
                    history_entry.status = 'Returned'
                    history_entry.return_date = now_datetime() 
                    
    transaction.status="Returned"
    transaction.save()
    if member:
        member.save()
    
    return {
        "message": "Books returned successfully"
    }
