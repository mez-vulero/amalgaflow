import frappe
import unittest

class TestExtensions(unittest.TestCase):
    def test_creation(self):
        doc = frappe.get_doc({
            'doctype': 'Extensions',
            'user_link': 'Administrator',
            'extension': '1001',
            'organization_id': 'ORG001',
        })
        doc.insert()
        self.assertEqual(doc.extension, '1001') 