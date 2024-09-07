# Copyright (c) 2024, David and contributors
# See license.txt

import frappe
import unittest

class TestGenre(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.existing_genre_name = "Science Fiction"
        if frappe.db.exists("Genre", self.existing_genre_name):
            frappe.delete_doc("Genre", self.existing_genre_name, ignore_permissions=True)

    def tearDown(self):
        """Clean up test data."""
        if frappe.db.exists("Genre", self.existing_genre_name):
            frappe.delete_doc("Genre", self.existing_genre_name, ignore_permissions=True)

    def test_genre_creation(self):
        """Test if a genre can be created successfully with valid data."""
        genre_name = "Science Fiction"
        if frappe.db.exists("Genre", genre_name):
            frappe.delete_doc("Genre", genre_name, ignore_permissions=True)

        genre = frappe.get_doc({
            "doctype": "Genre",
            "category_name": genre_name,
            "description": "A genre for Science Fiction books."
        })
        genre.insert()

        self.assertTrue(frappe.db.exists("Genre", genre_name))

    def test_unique_category_name(self):
        """Test if duplicate genre names are prevented."""
        genre_name = "Unique Genre"
        if frappe.db.exists("Genre", genre_name):
            frappe.delete_doc("Genre", genre_name, ignore_permissions=True)

        genre = frappe.get_doc({
            "doctype": "Genre",
            "category_name": genre_name,
            "description": "A genre with a unique name."
        })
        genre.insert()

        duplicate_genre = frappe.get_doc({
            "doctype": "Genre",
            "category_name": genre_name,
            "description": "Another genre with the same name."
        })
        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            duplicate_genre.insert()
