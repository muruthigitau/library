// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transaction", {
	refresh(frm) {
		if (frm.is_new()) {
			return;
		}

		// Calculate fees
		frappe.call({
			method: "library.library.doctype.transaction.transaction.calculate_fees",
			args: {
				transaction_name: frm.doc.name,
			},
			callback: function (response) {
				if (response.message) {
					frm.set_value("rent_fee_incurred", response.message.rent_fee_incurred);
					frm.set_value("late_fee_incurred", response.message.late_fee_incurred);
					frm.set_value("total_fee", response.message.total_fee);
				}
			},
		});

		// Update status if overdue
		if (frm.doc.status == "Issue" && frappe.datetime.get_today() > frm.doc.due_date) {
			frm.set_value("status", "Overdue");
			frm.save_or_update();
		}

		// Show overdue warning
		if (frm.doc.status == "Overdue") {
			frappe.msgprint({
				title: __("Overdue Warning"),
				indicator: "red",
				message: __("This issue is overdue. Please return it as soon as possible."),
			});
		}

		// Add "Return" button if not returned
		if (frm.doc.status !== "Returned") {
			frm.add_custom_button(__("Return"), function () {
				frm.set_value("status", "Returned");
				frm.save_or_update();
				frappe.msgprint({
					title: __("Book Returned"),
					indicator: "green",
					message: __("The book has been returned successfully."),
				});
			});
		}

		// Check if the total payments cover the total cost and update `doc.paid`
		update_payment_status(frm);

		// Show "Make Payment" button only if `doc.paid` is not 1
		if (frm.doc.paid !== 1 && frm.doc.status == "Returned") {
			frm.add_custom_button(__("Make Payment"), function () {
				show_payment_dialog(frm);
			});
		}
	},
});

function show_payment_dialog(frm) {
	let payment_dialog = new frappe.ui.Dialog({
		title: __("Make Payment"),
		fields: [
			{
				label: __("Amount"),
				fieldname: "amount",
				fieldtype: "Currency",
				default: frm.doc.total_fee,
			},
		],
		primary_action_label: __("Create Payment"),
		primary_action(values) {
			frappe.call({
				method: "frappe.client.insert",
				args: {
					doc: {
						doctype: "Payment",
						transaction: frm.doc.name,
						member: frm.doc.member,
						amount: values.amount,
						date_time: frappe.datetime.now_datetime(),
					},
				},
				callback: function (response) {
					if (response.message) {
						// Add the newly created payment to the payments child table
						let new_row = frm.add_child("payments"); // Assuming the child table field is "payments"
						new_row.payment = response.message.name; // Link the payment doc to the child table
						frm.refresh_field("payments"); // Refresh the payments child table to show the new row

						// Save the form to persist the changes
						frm.save().then(() => {
							// Update the payment status
							update_payment_status(frm).then(() => {
								frappe.msgprint({
									title: __("Payment Created"),
									indicator: "green",
									message: __(
										"A payment of {0} has been created for the transaction.",
										[values.amount]
									),
								});
							});
						});
					}
				},
			});

			payment_dialog.hide();
		},
	});

	payment_dialog.show();
}

function update_payment_status(frm) {
	const payments = frm.doc.payments.map((row) => row.payment);

	return frappe.call({
		method: "library.library.doctype.transaction.transaction.get_total_payments",
		args: {
			payments: payments,
		},
		callback: function (response) {
			if (response.message) {
				let total_payments = response.message.total_payments;
				let total_fee = frm.doc.total_fee;

				if (total_payments >= total_fee) {
					frm.set_value("paid", 1);
				} else {
					frm.set_value("paid", 0);
				}

				frm.save_or_update(); // Save the form after updating the paid status
			}
		},
	});
}
