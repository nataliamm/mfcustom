# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils import today, date_diff


@frappe.whitelist()
def get_balance(customer):
    fiscal_year = frappe.db.get_single_value('Global Defaults', 'current_fiscal_year')
    gl_entries = frappe.db.sql("""
        SELECT name, voucher_type, voucher_no,
            SUM(debit_in_account_currency) AS debit,
            SUM(credit_in_account_currency) AS credit,
            (
                CASE WHEN (voucher_type='Sales Invoice')
                    THEN (SELECT posting_date FROM `tabSales Invoice` WHERE name=voucher_no)
                WHEN (voucher_type='Payment Entry')
                    THEN (SELECT posting_date FROM `tabPayment Entry` WHERE name=voucher_no)
                WHEN (voucher_type='Journal Entry')
                    THEN (SELECT posting_date FROM `tabJournal Entry` WHERE name=voucher_no)
                END
            ) AS posting_date
        FROM `tabGL Entry`
        WHERE
            docstatus < 2
            AND party_type='Customer'
            AND party=%s
            AND fiscal_year=%s
        GROUP BY
            voucher_type,
            voucher_no,
            against_voucher_type,
            against_voucher, 
            party
        ORDER BY
            posting_date, name""", (customer,fiscal_year), as_dict=1)
    if gl_entries:
        current_balance = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) <= 30)
        less_sixty = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 31 and date_diff(today(), g.posting_date) <= 60)
        less_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 61 and date_diff(today(), g.posting_date) <= 90)
        above_ninety = sum(g.debit-g.credit for g in gl_entries if date_diff(today(), g.posting_date) > 91)
        frappe.db.set_value("Customer", customer, "current", current_balance)
        frappe.db.set_value("Customer", customer, "less_sixty", less_sixty)
        frappe.db.set_value("Customer", customer, "less_ninety", less_ninety)
        frappe.db.set_value("Customer", customer, "above_ninety", above_ninety)
    return True
