// Copyright (c) 2018, Mobile Fun Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Customer Statement', {
	refresh: function(frm) {
		return frappe.call({
			method: "get_customers",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("customers_table");
				frm.refresh_fields();
			}
		});
	}
});
