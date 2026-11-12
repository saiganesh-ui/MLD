import unittest
from ontology.ontology_manager import OntologyManager
from ontology.ontology_reasoner import OntologyReasoner
from database.models import Transaction, Account, Customer

class TestOntologyEngine(unittest.TestCase):
    def setUp(self):
        self.mgr = OntologyManager()
        self.reasoner = OntologyReasoner(self.mgr)

    def test_ontology_file_loading(self):
        self.assertIsNotNone(self.mgr.graph)
        self.assertGreater(len(self.mgr.graph), 0)

    def test_semantic_reasoning_high_risk(self):
        tx = Transaction(
            transaction_id="TX-ONT-1",
            sender_account="ACC-A",
            receiver_account="ACC-B",
            amount=50000.0,
            sender_country="Cayman Islands",
            receiver_country="United States"
        )
        s_acc = Account(account_number="ACC-A", customer_id="CUST-1", country="Cayman Islands")
        r_acc = Account(account_number="ACC-B", customer_id="CUST-2", country="United States")

        res = self.reasoner.evaluate_transaction(tx, s_acc, r_acc, None, None)
        self.assertTrue(res['is_suspicious'])
        self.assertIn("HighRiskCountry", str(res['inferences']))

    def test_semantic_reasoning_smurfing(self):
        tx = Transaction(
            transaction_id="TX-ONT-2",
            sender_account="ACC-A",
            receiver_account="ACC-B",
            amount=9200.0,
            sender_country="United States",
            receiver_country="United States"
        )
        s_acc = Account(account_number="ACC-A", customer_id="CUST-1", country="United States")
        r_acc = Account(account_number="ACC-B", customer_id="CUST-2", country="United States")

        res = self.reasoner.evaluate_transaction(tx, s_acc, r_acc, None, None)
        self.assertTrue(res['is_suspicious'])
        self.assertIn("SmurfingPattern", str(res['inferences']))

if __name__ == '__main__':
    unittest.main()
