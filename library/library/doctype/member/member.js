// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Member", {
	refresh(frm) {
		// Button to update total_books_borrowed
		frm.add_custom_button(__("Update Total Books Borrowed"), function () {
			frappe.call({
				method: "library.library.doctype.member.member.update_total_books_borrowed",
				args: {
					member_name: frm.doc.name,
				},
				callback: function (response) {
					if (response.message) {
						frm.set_value("total_books_borrowed", response.message);
						frm.refresh_field("total_books_borrowed");
						frappe.msgprint({
							title: __("Update Successful"),
							indicator: "green",
							message: __("Total books borrowed has been updated."),
						});
					}
				},
			});
		});

		// Button to update balance
		frm.add_custom_button(__("Update Balance"), function () {
			updateBalance(frm);
		});

		frm.add_custom_button(__("Make Payment"), function () {
			show_payment_dialog(frm);
		});
	},
});
function updateBalance(frm) {
	frappe.call({
		method: "library.library.doctype.member.member.update_debt",
		args: {
			member_name: frm.doc.name,
		},
		callback: function (response) {
			if (response.message) {
				frm.set_value("outstanding_debt", response.message);
				frm.refresh_field("outstanding_debt");
				frappe.msgprint({
					title: __("balance Updated"),
					indicator: "green",
					message: __("The member's balance has been updated."),
				});
			}
		},
	});
}
function show_payment_dialog(frm) {
	let payment_dialog = new frappe.ui.Dialog({
		title: __("Make Payment"),
		fields: [
			{
				label: __("Amount"),
				fieldname: "amount",
				fieldtype: "Currency",
				default: 0,
			},
		],
		primary_action_label: __("Create Payment"),
		primary_action(values) {
			frappe.call({
				method: "frappe.client.insert",
				args: {
					doc: {
						doctype: "Payment",
						member: frm.doc.name,
						amount: values.amount,
						date_time: frappe.datetime.now_datetime(),
					},
				},
				callback: function (response) {
					if (response.message) {
						frappe.msgprint({
							title: __("Payment Created"),
							indicator: "green",
							message: __("A payment of {0} has been created for the transaction.", [
								values.amount,
							]),
						});
						updateBalance(frm);
					}
				},
			});

			payment_dialog.hide();
		},
	});

	payment_dialog.show();
}
