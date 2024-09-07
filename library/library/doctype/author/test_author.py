# Copyright (c) 2024, David and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestAuthor(FrappeTestCase):
    def setUp(self):   
        if not frappe.db.exists("Author", "John Doe"):        
            self.author = frappe.get_doc({
                "doctype": "Author",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "1234567890",
                "address": "123 Main St"
            })
            self.author.insert()
        else:
            self.author = frappe.get_doc("Author", "John Doe")

    def test_author_creation(self):
        """Test if an author can be created successfully with valid data."""
        author = frappe.get_doc({
            "doctype": "Author",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "0987654321",
            "address": "456 Main St"
        })
        author.insert()
 
        self.assertEqual(author.first_name, "Jane")
        self.assertEqual(author.last_name, "Doe")
        self.assertEqual(author.email, "jane.doe@example.com")
        self.assertEqual(author.phone, "0987654321")
        self.assertEqual(author.address, "456 Main St")

    def test_required_fields(self):
        """Test validation of required fields like first_name and last_name."""   
        author = frappe.get_doc({
            "doctype": "Author",
            "last_name": "Smith",
            "email": "smith@example.com",
            "phone": "1231231234"
        })
        with self.assertRaises(frappe.exceptions.MandatoryError):
            author.insert()

        author = frappe.get_doc({
            "doctype": "Author",
            "first_name": "Emily",
            "email": "emily@example.com",
            "phone": "2342342345"
        })
        with self.assertRaises(frappe.exceptions.MandatoryError):
            author.insert()

    def test_duplicate_naming(self):
        """Test if duplicate author names based on auto-naming rule are prevented."""    
        author = frappe.get_doc({
            "doctype": "Author",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe.duplicate@example.com",
            "phone": "9876543210"
        })
  
        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            author.insert()

    def tearDown(self):    
        if frappe.db.exists("Author", "Jane Doe"):
            frappe.delete_doc("Author", "Jane Doe")
        if frappe.db.exists("Author", "John Doe"):
            frappe.delete_doc("Author", "John Doe")
