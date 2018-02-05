frappe.listview_settings['Batch Process'] = {
	onload: function(listview) {
	    frappe.route_options = {
		"status": ["!=", "Inactive"]
	    };
	}
};
