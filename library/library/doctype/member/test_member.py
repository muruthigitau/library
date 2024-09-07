
# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from .member import update_debt, update_total_books_borrowed

class TestMember(FrappeTestCase):
	def setUp(self):
		"""Create a sample Member and Book for testing."""		
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

		self.publisher_name = "Sample Publisher"
		self.author_first_name = "John"
		self.author_last_name = "Doe"
		
		if not frappe.db.exists("Publisher", self.publisher_name):
			frappe.get_doc({
				"doctype": "Publisher",
				"publisher_name": self.publisher_name
			}).insert()

		if not frappe.db.exists("Author", f"{self.author_first_name} {self.author_last_name}"):
			frappe.get_doc({
				"doctype": "Author",
				"first_name": self.author_first_name,
				"last_name": self.author_last_name
			}).insert()

		self.book_isbn = "987654321"
		book_name = f"{self.book_isbn} - Sample Book"
		if not frappe.db.exists("Book", book_name):
			self.book = frappe.get_doc({
				"doctype": "Book",
				"title": "Sample Book",
				"isbn": self.book_isbn,
				"publisher": self.publisher_name,
				"author": f"{self.author_first_name} {self.author_last_name}",
				"published_year": 2023,
				"language": "English",
				"available_copies": 10,
				"total_copies": 10,
				"cost": 500,
				"rent_fee_per_day": 50,
				"late_fee_rate": 10,
			})
			self.book.insert()
		else:
			self.book = frappe.get_doc("Book", book_name)

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
		frappe.get_doc({
			"doctype": "Borrowing History",
			"book": self.book.name,
			"date_borrowed": frappe.utils.now_datetime(),
			"status": "Issued",
			"copies": 1,
			"parent": self.member.name,  
			"parenttype": "Member"
		}).insert()

		frappe.get_doc({
			"doctype": "Borrowing History",
			"book": self.book.name,
			"date_borrowed": frappe.utils.now_datetime(),
			"status": "Issued",
			"copies": 2,
			"parent": self.member.name,  
			"parenttype": "Member"
		}).insert()

		update_total_books_borrowed(self.member.name)


	def test_update_debt(self):
		"""Test the update_debt method to correctly calculate outstanding debt."""		
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
			"amount": 200,
			"date_time": frappe.utils.now_datetime()  
		}).insert()

		frappe.get_doc({
			"doctype": "Payment",
			"member": self.member.name,
			"amount": 100,
			"date_time": frappe.utils.now_datetime()  
		}).insert()

		outstanding_debt = update_debt(self.member.name)
		updated_member = frappe.get_doc("Member", self.member.name)
		self.assertEqual(updated_member.outstanding_debt, 500)
		self.assertEqual(outstanding_debt, 500)



