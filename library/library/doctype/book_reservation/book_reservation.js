// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Book Reservation", {
	refresh(frm) {
		if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}
		if (frm.doc.status == "Reserved") {
			frm.add_custom_button(__("Cancel"), function () {
				frm.set_value("status", "Cancelled");
				frm.save().then(() => {
					frappe.msgprint(__("Reservation has been cancelled."));
				});
			}).addClass("btn-danger");
			if (!frm.doc.transaction) {
				frm.add_custom_button(__("Fulfill"), function () {
					frm.set_value("status", "Fulfilled");
					frm.save().then(() => {
						frappe.call({
							method: "library.library.doctype.book_reservation.book_reservation.create_transaction",
							args: {
								book_reservation_name: frm.doc.name,
							},
							callback: function (response) {
								if (response.message) {
									frm.set_value("transaction", response.message);
									frm.save().then(() => {
										frappe.msgprint(
											__(
												"Reservation has been fulfilled and transaction created."
											)
										);
										frappe.set_route("Form", "Transaction", response.message);
									});
								}
							},
						});
					});
				}).addClass("btn-success");
			}
		}
	},
});
