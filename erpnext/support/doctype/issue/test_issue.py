# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from erpnext.support.doctype.service_level_agreement.test_service_level_agreement import create_service_level_agreements_for_issues
from frappe.utils import now_datetime
import datetime
from datetime import timedelta
from frappe.desk.form import assign_to

class TestIssue(unittest.TestCase):
	def test_assignment(self):
		frappe.db.set_value('Customer', '_Test Customer', 'account_manager', 'test1@example.com')
		doc = make_issue(customer='_Test Customer')
		self.assertEqual(assign_to.get(dict(doctype = doc.doctype, name = doc.name))[0].get('owner'), 'test1@example.com')


	def test_response_time_and_resolution_time_based_on_different_sla(self):
		create_service_level_agreements_for_issues()

		creation = "2019-03-04 12:00:00"

		# make issue with customer specific SLA
		customer = create_customer("_Test Customer", "__Test SLA Customer Group", "__Test SLA Territory")
		issue = make_issue(creation, "_Test Customer")

		self.assertEquals(issue.response_by, datetime.datetime(2019, 3, 4, 14, 0))
		self.assertEquals(issue.resolution_by, datetime.datetime(2019, 3, 4, 15, 0))

		# make issue with customer_group specific SLA
		customer = create_customer("__Test Customer", "_Test SLA Customer Group", "__Test SLA Territory")
		issue = make_issue(creation, "__Test Customer")

		self.assertEquals(issue.response_by, datetime.datetime(2019, 3, 4, 14, 0))
		self.assertEquals(issue.resolution_by, datetime.datetime(2019, 3, 4, 15, 0))

		# make issue with territory specific SLA
		customer = create_customer("___Test Customer", "__Test SLA Customer Group", "_Test SLA Territory")
		issue = make_issue(creation, "___Test Customer")

		self.assertEquals(issue.response_by, datetime.datetime(2019, 3, 4, 14, 0))
		self.assertEquals(issue.resolution_by, datetime.datetime(2019, 3, 4, 15, 0))

		# make issue with default SLA
		issue = make_issue(creation)

		self.assertEquals(issue.response_by, datetime.datetime(2019, 3, 4, 16, 0))
		self.assertEquals(issue.resolution_by, datetime.datetime(2019, 3, 4, 18, 0))

		creation = "2019-03-04 14:00:00"
		# make issue with default SLA next day
		issue = make_issue(creation)

		self.assertEquals(issue.response_by, datetime.datetime(2019, 3, 4, 18, 0))
		self.assertEquals(issue.resolution_by, datetime.datetime(2019, 3, 6, 12, 0))

		frappe.flags.current_time = datetime.datetime(2019, 3, 4, 15, 0)

		issue.status = 'Closed'
		issue.save()

		self.assertEqual(issue.agreement_fulfilled, 'Fulfilled')

def make_issue(creation=None, customer=None):

	issue = frappe.get_doc({
		"doctype": "Issue",
		"subject": "Service Level Agreement Issue",
		"customer": customer,
		"raised_by": "test@example.com",
		"creation": creation
	}).insert(ignore_permissions=True)

	return issue

def create_customer(name, customer_group, territory):

	create_customer_group(customer_group)
	create_territory(territory)

	if not frappe.db.exists("Customer", {"customer_name": name}):
		frappe.get_doc({
			"doctype": "Customer",
			"customer_name": name,
			"customer_group": customer_group,
			"territory": territory
		}).insert(ignore_permissions=True)

def create_customer_group(customer_group):

	if not frappe.db.exists("Customer Group", {"customer_group_name": customer_group}):
		frappe.get_doc({
			"doctype": "Customer Group",
			"customer_group_name": customer_group
		}).insert(ignore_permissions=True)

def create_territory(territory):

	if not frappe.db.exists("Territory", {"territory_name": territory}):
		frappe.get_doc({
			"doctype": "Territory",
			"territory_name": territory,
		}).insert(ignore_permissions=True)
