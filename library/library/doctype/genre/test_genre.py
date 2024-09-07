# Copyright (c) 2024, David and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestGenre(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Genre", "Fiction"):
            self.genre = frappe.get_doc({
                "doctype": "Genre",
                "category_name": "Fiction",
                "description": "Fictional genre including novels, stories, etc."
            })
            self.genre.insert()
        else:
            self.genre = frappe.get_doc("Genre", "Fiction")

    def test_genre_creation(self):
        """Test if a genre can be created successfully with valid data."""
        genre = frappe.get_doc({
            "doctype": "Genre",
            "category_name": "Science Fiction",
            "description": "A genre dealing with imaginative and futuristic concepts."
        })
        genre.insert()
        
        self.assertEqual(genre.category_name, "Science Fiction")
        self.assertEqual(genre.description, "A genre dealing with imaginative and futuristic concepts.")

    def test_required_fields(self):
        """Test validation of required fields like category_name."""
        genre = frappe.get_doc({
            "doctype": "Genre",
            "description": "A genre with no name."
        })
        with self.assertRaises(frappe.exceptions.MandatoryError):
            genre.insert()

    def test_unique_category_name(self):
        """Test if duplicate genre names are prevented.""" 
        genre = frappe.get_doc({
            "doctype": "Genre",
            "category_name": "Fiction",  
            "description": "Duplicate genre."
        })

        with self.assertRaises(frappe.exceptions.UniqueValidationError):
            genre.insert()

    def tearDown(self):
        if frappe.db.exists("Genre", "Science Fiction"):
            frappe.delete_doc("Genre", "Science Fiction")
        if frappe.db.exists("Genre", "Fiction"):
            frappe.delete_doc("Genre", "Fiction")

