# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate


class BookReservation(Document):
	pass


@frappe.whitelist()
def create_transaction(book_reservation_name):
    
    book_reservation = frappe.get_doc("Book Reservation", book_reservation_name)
        
    if book_reservation.status == "Fulfilled":
        
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "book_list": book_reservation.book_list,
            "member": book_reservation.member,
            "date": nowdate(),  
        })
        
        
        transaction.insert()
        frappe.db.commit()  

        return transaction.name  
    else:
        frappe.throw(("Reservation is not fulfilled, cannot create transaction."))
