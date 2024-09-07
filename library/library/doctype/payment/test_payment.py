# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestPayment(FrappeTestCase):
    def setUp(self):
        self.member = frappe.get_doc({
            "doctype": "Member",
            "member_name": "Test Member",
            "email": "test@example.com"
        }).insert()

    def tearDown(self):
        frappe.delete_doc("Member", self.member.name)

    def test_payment_creation(self):
        payment = frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "amount": 500.0
        })
        payment.insert()

        self.assertEqual(payment.amount, 500.0)
        self.assertEqual(payment.member, self.member.name)

    def test_payment_autoname(self):
        payment = frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "amount": 500.0
        })
        payment.insert()

        expected_name = f"{self.member.name} - {payment.date_time} - Ksh. {payment.amount}"
        self.assertEqual(payment.name, expected_name)

    def test_payment_link_to_member(self):
        payment = frappe.get_doc({
            "doctype": "Payment",
            "member": self.member.name,
            "amount": 500.0
        })
        payment.insert()

        member = frappe.get_doc("Member", self.member.name)
        payments = [p.payment for p in member.payments]
        self.assertIn(payment.name, payments)
