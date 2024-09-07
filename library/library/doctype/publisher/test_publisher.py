# Copyright (c) 2024, David and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPublisher(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Publisher", "Test Publisher"):
            self.publisher = frappe.get_doc({
                "doctype": "Publisher",
                "publisher_name": "Test Publisher",
                "email": "test.publisher@example.com",
                "phone": "1234567890",
                "address": "123 Test St",
                "website": "https://testpublisher.com"
            })
            self.publisher.insert()
        else:
            self.publisher = frappe.get_doc("Publisher", "Test Publisher")

    def test_publisher_creation(self):
        """Test if a publisher can be created successfully with valid data."""
        publisher = frappe.get_doc({
            "doctype": "Publisher",
            "publisher_name": "Sample Publisher",
            "email": "sample.publisher@example.com",
            "phone": "0987654321",
            "address": "456 Sample St",
            "website": "https://samplepublisher.com"
        })
        publisher.insert()

        self.assertEqual(publisher.publisher_name, "Sample Publisher")
        self.assertEqual(publisher.email, "sample.publisher@example.com")
        self.assertEqual(publisher.phone, "0987654321")
        self.assertEqual(publisher.address, "456 Sample St")
        self.assertEqual(publisher.website, "https://samplepublisher.com")
        
    def test_required_fields(self):
        """Test validation of required fields like publisher_name."""
        publisher = frappe.get_doc({
			"doctype": "Publisher",
			"email": "publisher.without.name@example.com",
			"phone": "1122334455"
		})
        with self.assertRaises(frappe.ValidationError) as context:
            publisher.insert()

        self.assertTrue("Publisher Name is required" in str(context.exception))


    def test_unique_publisher_name(self):
        """Test if duplicate publisher names are prevented."""
        unique_publisher_name = "Unique Publisher Name"
        publisher = frappe.get_doc({
            "doctype": "Publisher",
            "publisher_name": unique_publisher_name,
            "email": "unique.publisher@example.com",
            "phone": "9876543210"
        })
        publisher.insert()

        duplicate_publisher = frappe.get_doc({
            "doctype": "Publisher",
            "publisher_name": unique_publisher_name,
            "email": "duplicate.publisher@example.com",
            "phone": "1234567890"
        })

        with self.assertRaises(frappe.exceptions.DuplicateEntryError):
            duplicate_publisher.insert()

    def tearDown(self):
        if frappe.db.exists("Publisher", "Sample Publisher"):
            frappe.delete_doc("Publisher", "Sample Publisher")
        if frappe.db.exists("Publisher", "Test Publisher"):
            frappe.delete_doc("Publisher", "Test Publisher")
