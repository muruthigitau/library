// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payment", {
	refresh(frm) {
		// Check if the "date_time" field is empty
		if (!frm.doc.date_time) {
			// Set the "date_time" field to the current date and time
			frm.set_value("date_time", frappe.datetime.now_datetime());
		}
	},
});
