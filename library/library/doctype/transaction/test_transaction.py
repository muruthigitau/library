# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import now_datetime, add_days

class TestTransaction(FrappeTestCase):
    def setUp(self):
        """Set up the necessary data for tests"""
        # Create a member
        self.member = frappe.get_doc({
            "doctype": "Member",
            "member_name": "Test Member"
        }).insert()

        # Create a book
        self.book = frappe.get_doc({
            "doctype": "Book",
            "title": "Test Book",
            "available_copies": 10,
            "rent_fee_per_day": 50,
            "late_fee_rate": 20
        }).insert()

    def test_create_transaction(self):
        """Test creating a new transaction"""
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "date": now_datetime(),
            "book_list": [{
                "book": self.book.name,
                "copies": 2
            }]
        })
        transaction.insert()

        # Check if the transaction was saved successfully
        self.assertEqual(transaction.docstatus, 0)
        self.assertEqual(transaction.member, self.member.name)
        self.assertEqual(len(transaction.book_list), 1)

    def test_calculate_fees(self):
        """Test calculating fees for a transaction"""
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "date": now_datetime(),
            "book_list": [{
                "book": self.book.name,
                "copies": 1
            }]
        }).insert()

        # Call calculate_fees method
        response = frappe.call("library.library.doctype.transaction.transaction.calculate_fees", transaction.name)

        rent_fee_incurred = response.get('rent_fee_incurred')
        late_fee_incurred = response.get('late_fee_incurred')
        total_fee = response.get('total_fee')

        # Assert that the fees are calculated correctly
        self.assertEqual(rent_fee_incurred, self.book.rent_fee_per_day)
        self.assertEqual(late_fee_incurred, 0)
        self.assertEqual(total_fee, rent_fee_incurred)

    def test_return_books(self):
        """Test returning books"""
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "date": now_datetime(),
            "book_list": [{
                "book": self.book.name,
                "copies": 1
            }]
        }).insert()

        # Call return_books method
        response = frappe.call("library.library.doctype.transaction.transaction.return_books", transaction.name)

        # Assert that the books were returned successfully
        self.assertEqual(response.get("message"), "Books returned successfully")

        # Verify that the transaction status is updated to 'Returned'
        transaction.reload()
        self.assertEqual(transaction.status, "Returned")

    def test_make_payment(self):
        """Test making a payment for a transaction"""
        transaction = frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "date": now_datetime(),
            "total_fee": 100,
            "book_list": [{
                "book": self.book.name,
                "copies": 1
            }]
        }).insert()

        # Simulate a payment
        payment = frappe.get_doc({
            "doctype": "Payment",
            "transaction": transaction.name,
            "member": transaction.member,
            "amount": 100,
            "date_time": now_datetime()
        }).insert()

        # Update payment status in the transaction
        frappe.call("library.library.doctype.transaction.transaction.get_total_payments", str([payment.name]))

        transaction.reload()
        self.assertEqual(transaction.paid, 1)

    def tearDown(self):
        """Clean up the created records"""
        frappe.delete_doc("Member", self.member.name)
        frappe.delete_doc("Book", self.book.name)
