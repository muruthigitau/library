# Copyright (c) 2024, David and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Payment(Document):
    def after_insert(self):
        if self.member:
            member = frappe.get_doc("Member", self.member)
            
            # Check if the payment already exists in the member's payments list
            existing_payment = next((p for p in member.payments if p.payment == self.name), None)
            
            if not existing_payment:
                # Append this payment to the member's payments list
                member.append("payments", {
                    "payment": self.name  # Link to the newly created payment
                })
                
                # Save the member with the updated payments list
                member.save()
            else:
                # Print a message for debugging purposes (you can remove or replace this with logging)
                print(f"Payment {self.name} already exists for member {self.member}.")

