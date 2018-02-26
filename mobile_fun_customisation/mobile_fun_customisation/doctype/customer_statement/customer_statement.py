# -*- coding: utf-8 -*-
# Copyright (c) 2018, Mobile Fun Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import fmt_money


class CustomerStatement(Document):
    def get_customers(self):
        gl_entries = frappe.db.sql("""
            SELECT name, posting_date, voucher_type, voucher_no,
                party_type, party,
                sum(debit_in_account_currency) AS debit,
                sum(credit_in_account_currency) AS credit,
                (SELECT debtor_id FROM tabCustomer WHERE name=party) AS debtor_id
            FROM `tabGL Entry`
            WHERE
                docstatus < 2
                and party_type='Customer'
            GROUP BY
                party
            ORDER BY
                party""", as_dict=1)
        primary_emails={g.party:frappe.db.sql("""SELECT email_id
                                    FROM tabContact
                                    WHERE name LIKE %s
                                        AND is_primary_contact=1""",("%%%s%%" % g.party), as_dict=1) for g in gl_entries}
        cc_emails={g.party:frappe.db.sql("""SELECT email_id
                                    FROM tabContact
                                    WHERE name LIKE %s
                                        AND is_primary_contact=0""",("%%%s%%" % g.party), as_list=1) for g in gl_entries}
        for i, emails in primary_emails.items():
            for g in gl_entries:
                if g.party == i and emails:
                    g.primary_emails = emails[0].email_id
        for i, emails in cc_emails.items():
            for g in gl_entries:
                if g.party == i and emails:
                    g.cc_emails = ','.join(str(r) for v in emails for r in v)

        for d in gl_entries:
            row = self.append('customers_table', {})
            d.customer = d.party
            d.email = d.primary_emails
            d.cc_email = d.cc_emails
            d.total_unpaid = fmt_money(d.debit - d.credit,2,"GBP")
            row.update(d)