// Copyright (c) 2024, David and contributors
// For license information, please see license.txt

frappe.query_reports["Stocks Balance"] = {
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
			fieldname: "posting_datetime",
			label: __("As Of Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(), // Default to today's date
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
