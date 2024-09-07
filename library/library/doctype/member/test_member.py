# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestMember(FrappeTestCase):

    def setUp(self):
        """Create a sample Member and Book for testing."""
        # Create a sample Member
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

        # Create a sample Book
        if not frappe.db.exists("Book", "123456789 - Sample Book"):
            self.book = frappe.get_doc({
                "doctype": "Book",
                "title": "Sample Book",
                "isbn": "123456789",
                "publisher": "Sample Publisher",
                "author": "Sample Author",
                "published_year": 2023,
                "language": "English",
                "available_copies": 10,
                "total_copies": 10,
                "cost": 500,
                "rent_fee_per_day": 50,
                "late_fee_rate": 10,
                "genre": ["Fiction", "Adventure"]  # Adding genres
            })
            self.book.insert()
        else:
            self.book = frappe.get_doc("Book", "123456789 - Sample Book")

    def test_member_creation(self):
        """Test if a member can be created and fields are validated."""
        member = frappe.get_doc({
            "doctype": "Member",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "phone": "0987654321",
            "date_of_membership": frappe.utils.nowdate(),
            "membership_status": "Active"
        })
        member.insert()

        self.assertEqual(member.first_name, "Jane")
        self.assertEqual(member.membership_status, "Active")

    def test_update_total_books_borrowed(self):
        """Test the update_total_books_borrowed method to correctly sum the books borrowed."""
        # Create borrowing history records
        frappe.get_doc({
            "doctype": "Borrowing History",
            "book": self.book.name,
            "date_borrowed": frappe.utils.now_datetime(),
            "status": "Issued",
            "copies": 1
        }).insert()

        frappe.get_doc({
            "doctype": "Borrowing History",
            "book": self.book.name,
            "date_borrowed": frappe.utils.now_datetime(),
            "status": "Issued",
            "copies": 2
        }).insert()

        # Assuming update_total_books_borrowed method exists
        total_books_borrowed = self.update_total_books_borrowed(self.member.name)

        # Retrieve updated member
        updated_member = frappe.get_doc("Member", self.member.name)

        self.assertEqual(updated_member.total_books_borrowed, 3)
        self.assertEqual(total_books_borrowed, 3)

    def test_update_debt(self):
        """Test the update_debt method to correctly calculate outstanding debt."""
        # Create transactions and payments
        frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "total_fee": 500
        }).insert()

        frappe.get_doc({
            "doctype": "Transaction",
            "member": self.member.name,
            "total_fee": 300
        }).insert()

        frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "amount": 200
        }).insert()

        frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "amount": 100
        }).insert()

        # Assuming update_debt method exists
        outstanding_debt = self.update_debt(self.member.name)

        # Retrieve updated member
        updated_member = frappe.get_doc("Member", self.member.name)

        self.assertEqual(updated_member.outstanding_debt, 500)
        self.assertEqual(outstanding_debt, 500)

    def update_total_books_borrowed(self, member_name):
        """Calculate total books borrowed."""
        total_borrowed = frappe.db.count("Borrowing History", filters={"member": member_name, "status": "Issued"})
        return total_borrowed

    def update_debt(self, member_name):
        """Calculate outstanding debt."""
        total_fee = frappe.db.sum("Transaction", "total_fee", filters={"member": member_name})
        total_payment = frappe.db.sum("Payment", "amount", filters={"member": member_name})
        return total_fee - total_payment

    def tearDown(self):
        """Clean up by deleting the test member and related data."""
        frappe.db.sql("DELETE FROM `tabBorrowing History` WHERE book = %s", (self.book.name))
        frappe.db.sql("DELETE FROM `tabTransaction` WHERE member = %s", (self.member.name))
        frappe.db.sql("DELETE FROM `tabPayment` WHERE member = %s", (self.member.name))
        self.book.delete()
        self.member.delete()
