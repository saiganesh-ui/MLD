import unittest
from datetime import datetime, timedelta
from database.models import Transaction, Account, Customer
from detection.rule_engine import RuleEngine
from detection.pattern_detector import PatternDetector
from config import Config

class TestDetectionRules(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()
        self.tx_large = Transaction(
            transaction_id="TX-TEST-01",
            sender_account="ACC-01",
            receiver_account="ACC-02",
            amount=75000.0,
            transaction_date=datetime.utcnow(),
            sender_country="United States",
            receiver_country="United States"
        )
        self.tx_normal = Transaction(
            transaction_id="TX-TEST-02",
            sender_account="ACC-01",
            receiver_account="ACC-02",
            amount=500.0,
            transaction_date=datetime.utcnow(),
            sender_country="United States",
            receiver_country="United States"
        )

    def test_large_transaction_rule(self):
        res = self.engine.rule_large_transaction(self.tx_large)
        self.assertTrue(res['detected'])
        self.assertEqual(res['score_contribution'], 25.0)

    def test_normal_transaction_rule(self):
        res = self.engine.rule_large_transaction(self.tx_normal)
        self.assertFalse(res['detected'])
        self.assertEqual(res['score_contribution'], 0.0)

    def test_structuring_rule(self):
        tx_struct = Transaction(
            transaction_id="TX-TEST-03",
            sender_account="ACC-01",
            receiver_account="ACC-02",
            amount=9500.0,
            transaction_date=datetime.utcnow(),
            sender_country="United States",
            receiver_country="United States"
        )
        recent = [
            Transaction(sender_account="ACC-01", amount=9200.0, transaction_date=datetime.utcnow() - timedelta(hours=1))
        ]
        res = self.engine.rule_structuring_smurfing(tx_struct, recent)
        self.assertTrue(res['detected'])

    def test_cross_border_rule(self):
        tx_cb = Transaction(
            transaction_id="TX-TEST-04",
            sender_account="ACC-01",
            receiver_account="ACC-02",
            amount=1000.0,
            transaction_date=datetime.utcnow(),
            sender_country="United States",
            receiver_country="Germany"
        )
        res = self.engine.rule_cross_border_activity(tx_cb)
        self.assertTrue(res['detected'])

    def test_high_risk_geography_rule(self):
        tx_hr = Transaction(
            transaction_id="TX-TEST-05",
            sender_account="ACC-01",
            receiver_account="ACC-02",
            amount=5000.0,
            transaction_date=datetime.utcnow(),
            sender_country="Panama",
            receiver_country="United States"
        )
        res = self.engine.rule_high_risk_geography(tx_hr)
        self.assertTrue(res['detected'])

if __name__ == '__main__':
    unittest.main()
