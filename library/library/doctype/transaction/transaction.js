// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transaction", {
	refresh(frm) {
		if (!frm.doc.date) {
			frm.set_value("date", frappe.datetime.get_today());
		}

		if (frm.is_new()) {
			return;
		}

		frm.add_custom_button(__("Update Fees"), function () {
			frappe.call({
				method: "library.library.doctype.transaction.transaction.calculate_fees",
				args: {
					transaction_name: frm.doc.name,
				},
				callback: function (response) {
					if (response.message) {
						update_payment_status(frm);
					}
				},
			});
		});

		if (frm.doc.status == "Issue" && frappe.datetime.get_today() > frm.doc.due_date) {
			frm.set_value("status", "Overdue");
			frm.save_or_update();
		}

		if (frm.doc.status == "Overdue") {
			frappe.msgprint({
				title: __("Overdue Warning"),
				indicator: "red",
				message: __("This issue is overdue. Please return it as soon as possible."),
			});
		}

		if (frm.doc.status !== "Returned") {
			frm.add_custom_button(__("Return Books"), function () {
				frappe.call({
					method: "library.library.doctype.transaction.transaction.return_books",
					args: {
						transaction_name: frm.doc.name,
					},
					callback: function (response) {
						if (response.message) {
							frm.refresh();
							frappe.msgprint({
								title: __("Books Returned"),
								indicator: "green",
								message: __("The books have been successfully returned."),
							});
						}
					},
				});
			});
		}

		if (frm.doc.paid !== 1 && frm.doc.status == "Returned") {
			frm.add_custom_button(__("Make Payment"), function () {
				show_payment_dialog(frm);
			});
		}
	},

	member: function (frm) {
		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "My Settings",
				name: "My Settings",
			},
			callback: function (response) {
				if (response.message) {
					let max_debt_limit = response.message.max_debt_limit;

					// Call the update_debt method and check against max_debt_limit
					frappe.call({
						method: "library.library.doctype.member.member.update_debt",
						args: {
							member_name: frm.doc.member,
						},
						callback: function (response) {
							let total_debt = response.message;

							if (total_debt > max_debt_limit) {
								// Disable the save button
								frm.disable_save();
								frappe.throw({
									title: __("Debt Limit Exceeded"),
									message: __(
										"The member's total debt exceeds the limit of Ksh. " +
											max_debt_limit +
											". Please clear outstanding payments before proceeding."
									),
								});
							}
						},
					});
				}
			},
		});
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
						let new_row = frm.add_child("payments");
						new_row.payment = response.message.name;
						frm.refresh_field("payments");

						frm.save().then(() => {
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

				frm.save_or_update();
			}
		},
	});
}
