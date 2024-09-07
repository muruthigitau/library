# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Book(Document):
	def before_save(self):
		if self.is_new():
			self.available_copies = self.total_copies
