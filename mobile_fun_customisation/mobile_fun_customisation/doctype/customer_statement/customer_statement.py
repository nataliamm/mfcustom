# -*- coding: utf-8 -*-
# Copyright (c) 2018, Mobile Fun Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json


from frappe.model.document import Document
from frappe.utils import fmt_money, today, formatdate
from frappe import _


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
        primary_emails={g.party:frappe.db.sql("""SELECT email_id, first_name, last_name
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
                    if emails[0].last_name:
                        g.contact_name = emails[0].first_name + " " + emails[0].last_name
                    else:
                        g.contact_name = emails[0].first_name
        for i, emails in cc_emails.items():
            for g in gl_entries:
                if g.party == i and emails:
                    g.cc_emails = ','.join(str(r) for v in emails for r in v)

        for d in gl_entries:
            d.total_unpaid = fmt_money(d.debit - d.credit, 2, "GBP")
            if d.total_unpaid != 0:
                row = self.append('customers_table', {})
                d.customer_name = d.party
                d.email = d.primary_emails
                d.cc_email = d.cc_emails
                d.total_unpaid = fmt_money(d.debit - d.credit, 2, "GBP")
                row.update(d)


@frappe.whitelist()
def send_statements(checked_customers, sending_date):
    customers = json.loads(checked_customers)
    sending_date = formatdate(sending_date, 'dd/MM/YYYY')
    standard_reply = frappe.db.sql("""SELECT response
        FROM `tabStandard Reply`
        where name='Statement'""",as_dict=1)
    for i in customers:
        if i.get("email"):
            attachments = [frappe.attach_print("Customer", i.get("customer_name"), print_format="Customer Statement")]
            message = standard_reply[0].response.replace("{ contact_name }", i.get("contact_name")).replace("{ statement_date }", sending_date)
            frappe.sendmail(i.get("email"),
                subject=_("Statement of Account for {0} as of {1}").format(i.get("customer_name"), sending_date),
                message=message,
                cc=i.get("cc_email") or [],
                attachments=attachments
            )
    return True
