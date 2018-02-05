# Copyright (c) 2013, Mobile Fun Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext import get_default_currency
from frappe.model.meta import get_field_precision

def execute(filters=None):
	columns = get_column()
	args = get_args()
	data = get_data(args)
	return columns, data

def get_column():
	return [
		_("Purchase Order") + ":Link/Purchase Receipt:120", _("Date") + ":Date:100",
		_("Creditor ID") + ":Link/Customer:120", _("Supplier Name") + "::120", _("Currency") + "::100",
		_("Item Code") + ":Link/Item:120", _("Item Name") + "::120", _("Item Cost") + "::100", _("Item Qty") + "::100",
		_("Originating Amount") + "::100", _("Originating Billed Amount") + "::100", _("Originating Amount to Bill") + "::100",
		_("Functional Amount") + "::100", _("Functional Billed Amount") + "::100", _("Functional Amount to Bill") + "::100"
	]

def get_args():
	return {'doctype': 'Purchase Receipt', 'party': 'supplier',
		'date': 'posting_date', 'order': 'name', 'order_by': 'desc'}

def get_data(args):
	doctype, party = args.get('doctype'), args.get('party')
	child_tab = doctype + " Item"

	return frappe.db.sql("""
		Select
			`{parent_tab}`.purchase_order_id, `{parent_tab}`.{date_field}, `{parent_tab}`.creditor_id, `{parent_tab}`.{party}_name, `{parent_tab}`.currency,
			`{child_tab}`.item_code, `{child_tab}`.item_name, format(`{child_tab}`.rate,2), `{child_tab}`.received_qty,
			format(`{child_tab}`.amount,2), format(ifnull(`{child_tab}`.billed_amt,0),2), format(`{child_tab}`.amount - ifnull(`{child_tab}`.billed_amt, 0),2),
			format(`{child_tab}`.base_amount,2), format(ifnull(`{child_tab}`.billed_amt * `{parent_tab}`.conversion_rate,0),2),
			format(`{child_tab}`.base_amount - ifnull(`{child_tab}`.billed_amt * `{parent_tab}`.conversion_rate, 0),2)
		from
			`{parent_tab}`, `{child_tab}`
		where
			`{parent_tab}`.name = `{child_tab}`.parent and `{parent_tab}`.docstatus = 1 and `{parent_tab}`.status != 'Closed'
			and `{child_tab}`.amount > 0 and `{child_tab}`.billed_amt < `{child_tab}`.base_amount
		group by
			`{parent_tab}`.name, `{child_tab}`.item_code, `{child_tab}`.received_qty
		order by
			`{parent_tab}`.{order} {order_by}
		""".format(parent_tab = 'tab' + doctype, child_tab = 'tab' + child_tab, party = party,
			date_field = args.get('date'), order= args.get('order'), order_by = args.get('order_by')))
