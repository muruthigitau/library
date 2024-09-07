# Copyright (c) 2024, David and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestPayment(FrappeTestCase):
	def setUp(self):
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

	def test_payment_creation(self):
		payment = frappe.get_doc({
			"doctype": "Payment",
			"member": self.member.name,
			"date_time": frappe.utils.now_datetime(),
			"amount": 500.0
		})
		payment.insert()

		self.assertEqual(payment.amount, 500.0)


	def test_payment_link_to_member(self):
		payment = frappe.get_doc({
			"doctype": "Payment",
			"member": self.member.name,
			"date_time": frappe.utils.now_datetime(),
			"amount": 500.0
		})
		payment.insert()

		member = frappe.get_doc("Member", self.member.name)
		payments = [p.payment for p in member.payments]
		self.assertIn(payment.name, payments)
