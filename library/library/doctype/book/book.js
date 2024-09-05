// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.ui.form.on("Book", {
	refresh(frm) {
		// Add a custom button to reserve the book
		frm.add_custom_button(__("Reserve Book"), function () {
			// Open a prompt to select the member
			frappe.prompt(
				[
					{
						fieldname: "member",
						fieldtype: "Link",
						options: "Member", // Assuming you have a "Member" doctype
						label: "Select Member",
						reqd: 1,
					},
				],
				function (values) {
					// Create a book entry with name and copies
					let book_entry = {
						book: frm.doc.name,
						copies: 1,
					};

					// Create a new Book Reservation and save it with the selected member
					frappe.db
						.insert({
							doctype: "Book Reservation",
							book_list: [book_entry],
							member: values.member,
							date: frappe.datetime.get_today(),
						})
						.then(function (reservation) {
							// Open the newly created Book Reservation
							frappe.set_route("Form", "Book Reservation", reservation.name);
						});
				},
				__("Select Member"),
				__("Create Reservation")
			);
		}).addClass("btn-primary");
	},
});
