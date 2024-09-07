# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestBook(FrappeTestCase):

    def setUp(self):
        """Create sample genres and a sample Book for testing."""
        # Create genres
        self.genres = ["Fiction", "Adventure", "Non-Fiction", "Biography"]
        for genre in self.genres:
            if not frappe.db.exists("Genre", genre):
                frappe.get_doc({
                    "doctype": "Genre",
                    "category_name": genre
                }).insert()

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

    def test_book_creation(self):
        """Test if a book can be created and fields are validated."""
        book = frappe.get_doc({
            "doctype": "Book",
            "title": "Another Book",
            "isbn": "987654321",
            "publisher": "Another Publisher",
            "author": "Another Author",
            "published_year": 2024,
            "language": "Swahili",
            "available_copies": 5,
            "total_copies": 5,
            "cost": 600,
            "rent_fee_per_day": 60,
            "late_fee_rate": 15,
            "genre": ["Non-Fiction", "Biography"]  # Adding genres
        })
        book.insert()

        self.assertEqual(book.title, "Another Book")
        self.assertEqual(book.isbn, "987654321")
        self.assertEqual(book.publisher, "Another Publisher")
        self.assertEqual(book.author, "Another Author")
        self.assertEqual(book.language, "Swahili")
        self.assertEqual(book.available_copies, 5)
        self.assertEqual(book.total_copies, 5)
        self.assertEqual(book.cost, 600)
        self.assertEqual(book.rent_fee_per_day, 60)
        self.assertEqual(book.late_fee_rate, 15)
        self.assertEqual(book.genre, ["Non-Fiction", "Biography"])  # Verify the genres

    def test_before_save(self):
        """Test the before_save method to initialize available copies."""
        self.book.total_copies = 20
        self.book.save()
        self.assertEqual(self.book.available_copies, 20)

    def tearDown(self):
        """Clean up by deleting the test book and genres."""
        self.book.delete()
        for genre in self.genres:
            if frappe.db.exists("Genre", genre):
                frappe.get_doc("Genre", genre).delete()
