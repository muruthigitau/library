import frappe
from frappe.tests.utils import FrappeTestCase

class TestBook(FrappeTestCase):

	def setUp(self):
		"""Create sample genres, authors, publishers, and a sample Book for testing."""
		self.genres = ["Fiction", "Adventure", "Non-Fiction", "Biography"]
		for genre in self.genres:
			if not frappe.db.exists("Genre", genre):
				frappe.get_doc({
					"doctype": "Genre",
					"category_name": genre
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

		if not frappe.db.exists("Book", "123456789 - Sample Book"):
			self.book = frappe.get_doc({
				"doctype": "Book",
				"title": "Sample Book",
				"isbn": "123456789",
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
			self.book = frappe.get_doc("Book", "123456789 - Sample Book")

	def test_book_creation(self):
		"""Test if a book can be created and fields are validated."""
		book = frappe.get_doc({
			"doctype": "Book",
			"title": "Another Book",
			"isbn": "987654321",
			"publisher": self.publisher_name,
			"author": f"{self.author_first_name} {self.author_last_name}",
			"published_year": 2024,
			"language": "Swahili",
			"available_copies": 5,
			"total_copies": 5,
			"cost": 600,
			"rent_fee_per_day": 60,
			"late_fee_rate": 15,
		})
		book.insert()

		self.assertEqual(book.title, "Another Book")
		self.assertEqual(book.isbn, "987654321")
		self.assertEqual(book.publisher, self.publisher_name)
		self.assertEqual(book.author, f"{self.author_first_name} {self.author_last_name}")
		self.assertEqual(book.language, "Swahili")
		self.assertEqual(book.available_copies, 5)
		self.assertEqual(book.total_copies, 5)
		self.assertEqual(book.cost, 600)
		self.assertEqual(book.rent_fee_per_day, 60)
		self.assertEqual(book.late_fee_rate, 15)

	def test_before_save(self):
		"""Test the before_save method to initialize available copies."""
		if not self.book.name:
			self.book.total_copies = 20
			self.book.save()
			
			self.book.reload()
			
			self.assertEqual(self.book.available_copies, self.book.total_copies)

	def tearDown(self):
		"""Clean up by deleting the test book and genres."""
		if frappe.db.exists("Book", "123456789 - Sample Book"):
			frappe.get_doc("Book", "123456789 - Sample Book").delete()

