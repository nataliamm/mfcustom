import frappe
from erpnext.buying.doctype.purchase_order.purchase_order import make_purchase_receipt
from frappe.utils.data import get_time

def create_purchase_receipt(doc, model):
	po = frappe.get_doc({
		"doctype": "Purchase Order",
		"name": doc.name,
		"transaction_date": doc.transaction_date
	})

	pr = make_purchase_receipt(po.name)
	pr.posting_date = po.transaction_date
	pr.posting_time = get_time("00:00:00")
	pr.set_posting_time = 1
	pr.save()
	pr.submit()
