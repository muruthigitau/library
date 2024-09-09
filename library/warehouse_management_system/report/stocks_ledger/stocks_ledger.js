// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.query_reports["Stocks Ledger"] = {
	filters: [
		{
			fieldname: "product",
			label: __("Product"),
			fieldtype: "Link",
			options: "Product",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
	],

	onload: function (report) {
		report.page.add_inner_button(__("Clear Filters"), function () {
			report.filters.forEach(function (filter) {
				filter.set_value("");
			});

			report.refresh();
		});
	},
};
