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
	},
	send: function(frm) {
		var checked_customers = [];
		$.each(frm.doc.customers_table, function(i, customer) {
            if(customer.__checked == 1) {
            	var customers = {}
                customers["customer_name"] = customer.customer_name;
                customers["debtor_id"] = customer.debtor_id;
                customers["total_unpaid"] = customer.total_unpaid;
                customers["email"] = customer.email;
                customers["cc_email"] = customer.cc_email;
            	checked_customers.push(customers)
            }
        })
		frappe.call({
			method: "mobile_fun_customisation.mobile_fun_customisation.doctype.customer_statement.customer_statement.send_statements",
			args: {
				checked_customers: checked_customers,
			},
			callback: function(r) {
				if(!r.exc) {
					msgprint("Emails have been sent")
				}
				frm.refresh_fields();
			}
		});
	}
});
