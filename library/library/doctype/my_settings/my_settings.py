# Copyright (c) 2024, David and contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestMySettings(FrappeTestCase):

    def setUp(self):
        # Ensure there is always a MySettings document to work with
        if not frappe.db.exists("My Settings"):
            self.settings = frappe.get_doc({
                "doctype": "My Settings",
                "max_debt_limit": 5000.00,
                "late_fee_per_day": 50.00,
                "max_lease_days": 30
            })
            self.settings.insert()
        else:
            self.settings = frappe.get_doc("My Settings")

    def test_max_debt_limit(self):
        """Test if the Max Debt Limit is correctly set and retrieved."""
        self.settings.max_debt_limit = 10000.00
        self.settings.save()

        # Fetch the updated settings and check the value
        settings = frappe.get_doc("My Settings")
        self.assertEqual(settings.max_debt_limit, 10000.00)

    def test_late_fee_per_day(self):
        """Test if the Late Fee Per Day is correctly set and retrieved."""
        self.settings.late_fee_per_day = 75.00
        self.settings.save()

        # Fetch the updated settings and check the value
        settings = frappe.get_doc("My Settings")
        self.assertEqual(settings.late_fee_per_day, 75.00)

    def test_max_lease_days(self):
        """Test if the Max Lease Days is correctly set and retrieved."""
        self.settings.max_lease_days = 45
        self.settings.save()

        # Fetch the updated settings and check the value
        settings = frappe.get_doc("My Settings")
        self.assertEqual(settings.max_lease_days, 45)

    def tearDown(self):
        # Optionally reset the settings to their defaults after testing
        self.settings.max_debt_limit = 5000.00
        self.settings.late_fee_per_day = 50.00
        self.settings.max_lease_days = 30
        self.settings.save()

