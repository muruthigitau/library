# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate
from .book_reservation import create_transaction  # Adjust the import path accordingly

class TestBookReservation(FrappeTestCase):
    
	def setUp(self):
		"""Set up sample data for testing."""
		# Create a sample member for reservation with mandatory fields
		self.member_name = "John Doe"
		if not frappe.db.exists("Member", self.member_name):
			frappe.get_doc({
				"doctype": "Member",
				"first_name": "John",
				"last_name": "Doe",
				"date_of_membership": nowdate(),
				"email": "test@example.com",
				"phone": "1234567890"
			}).insert()

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

		# Create a sample Book Reservation
		self.book_reservation_name = "Test Reservation"
		if not frappe.db.exists("Book Reservation", self.book_reservation_name):
			reservation = frappe.get_doc({
				"doctype": "Book Reservation",
				"member": self.member_name,
				"status": "Fulfilled",
				"date": nowdate(),
				"book_list": [{"book": book_name}]  
			}).insert()
			self.book_reservation_name = reservation.name

	def test_create_transaction(self):
		"""Test if a transaction is created successfully from a fulfilled reservation."""
		transaction_name = create_transaction(self.book_reservation_name)
		transaction = frappe.get_doc("Transaction", transaction_name)
		
		self.assertEqual(transaction.member, self.member_name)
		self.assertEqual(transaction.date, nowdate())

	def test_create_transaction_unfulfilled(self):
		"""Test that creating a transaction fails if the reservation status is not fulfilled."""
		# Update the reservation status to "Pending"
		book_reservation = frappe.get_doc("Book Reservation", self.book_reservation_name)
		book_reservation.status = "Pending"
		book_reservation.save()
		
		with self.assertRaises(frappe.exceptions.ValidationError) as context:
			create_transaction(self.book_reservation_name)
		
		self.assertEqual(
			str(context.exception),
			"Reservation is not fulfilled, cannot create transaction."
		)

	def tearDown(self):
		"""Clean up by deleting the test documents."""
		if frappe.db.exists("Book Reservation", self.book_reservation_name):
			frappe.get_doc("Book Reservation", self.book_reservation_name).delete()
		


