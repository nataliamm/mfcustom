# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import today, date_diff


@frappe.whitelist()
def get_balance(customer):
    fiscal_year = frappe.db.get_single_value('Global Defaults', 'current_fiscal_year')
    gl_entries = frappe.db.sql("""
        select name, voucher_type, voucher_no,
            sum(debit_in_account_currency) as debit,
            sum(credit_in_account_currency) as credit,
            (
                case when (voucher_type='Sales Invoice')
                    then (select posting_date from `tabSales Invoice` where name=voucher_no)
                when (voucher_type='Payment Entry')
                    then (select posting_date from `tabPayment Entry` where name=voucher_no)
                when (voucher_type='Journal Entry')
                    then (select posting_date from `tabJournal Entry` where name=voucher_no)
                end
            ) as posting_date
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
    less_sixty = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 31 and date_diff(today(), g.posting_date) <= 60)
    less_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 61 and date_diff(today(), g.posting_date) <= 90)
    above_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 91)
    frappe.db.set_value("Customer", customer, "current", current_balance)
    frappe.db.set_value("Customer", customer, "less_sixty", less_sixty)
    frappe.db.set_value("Customer", customer, "less_ninety", less_ninety)
    frappe.db.set_value("Customer", customer, "above_ninety", above_ninety)
    return True
