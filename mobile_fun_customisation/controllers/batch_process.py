# -*- coding: utf-8 -*-
# Copyright (c) 2017, Mobile Fun Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from frappe import _

class BatchProcess(Document):
        pass

@frappe.whitelist()
def count_docs(type, filter):
       count = frappe.db.count(type, filters={"batch_id":("=", filter)})
       return count

@frappe.whitelist()
def submit_documents(doc):
	doc_dict = json.loads(doc)
	if 'batch_docs' in doc_dict and len(doc_dict['batch_docs']) != 0:
		doc_list = doc_dict['batch_docs']
		for i in range(0, len(doc_list)):
			d = frappe.get_doc(doc_dict['batch_type'], doc_list[i]['document_name'])
			d.submit()
		frappe.msgprint("Documents submitted")

		doc_name = doc_dict['name']
		x = frappe.get_doc('Batch Process', doc_name)
		x.status = 'Inactive'
		x.save()
	else:
		frappe.msgprint("This batch is empty")

# Count number of documents posted or in draft with the current batch ID and set the status accordingly

@frappe.whitelist()
def update_status(doc):
	doc_dic = json.loads(doc)
	doc_nam = doc_dic['name']
	doc_doc = frappe.get_doc('Batch Process', doc_nam)
	doc_cnt = count_docs(doc_dic['batch_type'], doc_dic['batch_id'])
	doc_len = len(doc_dic['batch_docs'])
	doc_sta = doc_doc.status
	if doc_cnt != 0 and doc_len != 0 and doc_sta != 'Active':
		doc_doc.status = 'Active'
		doc_doc.save()
	elif doc_cnt == 0 and doc_len != 0 and doc_sta != 'Active':
		doc_doc.status = 'Active'
		doc_doc.save()
	elif doc_cnt != 0 and doc_len == 0 and doc_sta != 'Inactive':
		doc_doc.status = 'Inactive'
		doc_doc.save()
	elif doc_cnt == 0 and doc_len == 0 and doc_sta != 'Empty':
		doc_doc.status = 'Empty'
		doc_doc.save()

# DELETE only empties child tables for batches that match the current doctype
# Update the INSERT statement with relevent fields for each doctype

@frappe.whitelist()
def purchase_invoice_batch_update(a, b):
	batch_list = frappe.get_list('Batch Process')
	for doc in batch_list:
		frappe.db.sql("""DELETE FROM `tabBatch Process Documents` WHERE batch_type = 'Purchase Invoice'""")
		frappe.db.sql("""INSERT INTO `tabBatch Process Documents` SELECT name AS name, %s AS creation, NOW() AS modified, %s AS modified_by, %s AS owner, docstatus, batch_id AS parent, 'batch_docs' AS parentfield, 'Batch Process' AS parenttype, 1 AS idx, bill_no AS document_name, bill_date AS document_date, 'Purchase Invoice' AS batch_type FROM `tabPurchase Invoice` WHERE docstatus = 0""", (a.creation, a.modified_by, a.owner))
	for doc in batch_list:
                i = frappe.get_doc('Batch Process', doc)
                j = frappe.get_doc('Batch Process', doc).as_json()
		update_status(j)

@frappe.whitelist()
def journal_entry_batch_update(a, b):
        batch_list = frappe.get_list('Batch Process')
        for doc in batch_list:
                frappe.db.sql("""DELETE FROM `tabBatch Process Documents` WHERE batch_type = 'Journal Entry'""")
                frappe.db.sql("""INSERT INTO `tabBatch Process Documents` SELECT name AS name, %s AS creation, NOW() AS modified, %s AS modified_by, %s AS owner, docstatus, batch_id AS parent, 'batch_docs' AS parentfield, 'Batch Process' AS parenttype, 1 AS idx, name AS document_name, posting_date AS document_date, 'Journal Entry' AS batch_type FROM `tabJournal Entry` WHERE docstatus = 0""", (a.creation, a.modified_by, a.owner))
        for doc in batch_list:
                i = frappe.get_doc('Batch Process', doc)
                j = frappe.get_doc('Batch Process', doc).as_json()
                update_status(j)

@frappe.whitelist()
def purchase_order_batch_update(a, b):
        batch_list = frappe.get_list('Batch Process')
        for doc in batch_list:
                frappe.db.sql("""DELETE FROM `tabBatch Process Documents` WHERE batch_type = 'Purchase Order'""")
                frappe.db.sql("""INSERT INTO `tabBatch Process Documents` SELECT name AS name, %s AS creation, NOW() AS modified, %s AS modified_by, %s AS owner, docstatus, batch_id AS parent, 'batch_docs' AS parentfield, 'Batch Process' AS parenttype, 1 AS idx, name AS document_name, transaction_date AS document_date, 'Purchase Order' AS batch_type FROM `tabPurchase Order` WHERE docstatus = 0""", (a.creation, a.modified_by, a.owner))
        for doc in batch_list:
                i = frappe.get_doc('Batch Process', doc)
                j = frappe.get_doc('Batch Process', doc).as_json()
                update_status(j)
