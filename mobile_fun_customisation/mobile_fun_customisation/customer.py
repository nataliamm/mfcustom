# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import today, date_diff


@frappe.whitelist()
def get_balance(customer):
    fiscal_year = frappe.db.get_single_value('Global Defaults', 'current_fiscal_year')
    gl_entries = frappe.db.sql("""
        select name, posting_date, voucher_type, voucher_no,
            against_voucher_type, against_voucher, 
            sum(debit_in_account_currency) as debit, 
            sum(credit_in_account_currency) as credit
        from `tabGL Entry`
        where
            docstatus < 2
            and party_type='Customer'
            and party=%s
            and fiscal_year=%s
        group by
            voucher_type,
            voucher_no,
            against_voucher_type,
            against_voucher, 
            party
        order by
            posting_date, name""", (customer,fiscal_year), as_dict=1)
    current_balance = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) <= 30)
    if current_balance:
        frappe.db.set_value("Customer",customer,"current", current_balance)
    less_sixty = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 31 and date_diff(today(), g.posting_date) <= 60)
    if less_sixty:
        frappe.db.set_value("Customer",customer,"current", less_sixty)
    less_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 61 and date_diff(today(), g.posting_date) <= 90)
    if less_ninety:
        frappe.db.set_value("Customer",customer,"current", less_ninety)
    above_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 91)
    if above_ninety:
        frappe.db.set_value("Customer",customer,"current", above_ninety)
    return True
