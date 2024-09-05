# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Member(Document):
	pass


@frappe.whitelist()
def update_total_books_borrowed(member_name):
    """
    Update the total_books_borrowed field for the member based on the total copies borrowed.
    Args:
        member_name (str): The name of the member.
    Returns:
        float: The updated total books borrowed value.
    """
    member = frappe.get_doc("Member", member_name)
    total_books_borrowed = sum(entry.copies for entry in member.borrowing_history)
    
    # Update the total_books_borrowed field
    member.total_books_borrowed = total_books_borrowed
    member.save()

    return total_books_borrowed

@frappe.whitelist()
def update_debt(member_name):
    """
    Update the outstanding_debt field for the member based on unpaid fees and payments.
    Args:
        member_name (str): The name of the member.
    Returns:
        float: The updated outstanding_debt value.
    """
    # Fetch the member document
    member = frappe.get_doc("Member", member_name)

    # Calculate total fees from transactions
    total_fees = frappe.db.sql("""
        SELECT SUM(total_fee)
        FROM `tabTransaction`
        WHERE member = %s 
    """, (member_name), as_dict=True)[0]['SUM(total_fee)'] or 0

    # Calculate total payments made by the member
    total_payments = frappe.db.sql("""
        SELECT SUM(amount)
        FROM `tabPayment`
        WHERE member = %s
    """, (member_name), as_dict=True)[0]['SUM(amount)'] or 0

    # Calculate outstanding debt
    outstanding_debt = total_fees - total_payments

    # Update the member's outstanding_debt field
    member.outstanding_debt = outstanding_debt
    member.save()

    return outstanding_debt

