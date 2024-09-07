# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days
from library.library.doctype.transaction.transaction import calculate_fees, get_total_payments, return_books

class TestTransaction(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Member", "John Doe"):
            self.member = frappe.get_doc({
                "doctype": "Member",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "date_of_membership": frappe.utils.nowdate(),
                "membership_status": "Active"
            })
            self.member.insert() 
        else:
            self.member = frappe.get_doc("Member", "John Doe")
        

        self.transaction = frappe.get_doc({
            "doctype": "Transaction",
            "date": now_datetime(),
            "member": self.member.name
        })
        self.transaction.insert()


    def test_calculate_fees(self):
        fees = calculate_fees(self.transaction.name)
        expected_rent_fee = 0  
        self.assertEqual(fees['rent_fee_incurred'], expected_rent_fee)
        self.assertEqual(fees['late_fee_incurred'], 0)
        self.assertEqual(fees['total_fee'], expected_rent_fee)

    def test_return_books(self):
        return_result = return_books(self.transaction.name)
        self.assertEqual(return_result['message'], "Books returned successfully")
        
        
        transaction = frappe.get_doc("Transaction", self.transaction.name)
        self.assertEqual(transaction.status, "Returned")
        for entry in transaction.book_list:
            self.assertEqual(entry.status, "Returned")
        

    def test_get_total_payments(self):
        
        payment1 = frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "date_time": now_datetime(),
            "amount": 100.0
        }).insert()

        payment2 = frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "date_time": now_datetime(),
            "amount": 200.0
        }).insert()

        payments_list = [payment1.name, payment2.name]
        total_payments = get_total_payments(str(payments_list))
        self.assertEqual(total_payments['total_payments'], 300.0)
