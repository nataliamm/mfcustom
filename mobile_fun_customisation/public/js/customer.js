frappe.ui.form.on("Customer", {
	refresh: function(frm) {
		console.log('test')
		if(!frm.doc.__islocal) {
			frappe.call({
				type: "POST",
				method: "mobile_fun_customisation.mobile_fun_customisation.customer.get_balance",
				args: {
					"customer": frm.doc.name
				},
				callback: function(r) {
					if(!r.exc && r.message) {
					}
				}
			})
		}
	}
})
