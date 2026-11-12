from detection.rule_engine import RuleEngine
from detection.anomaly_detector import AnomalyDetector
from ontology.ontology_reasoner import OntologyReasoner
from detection.pattern_detector import PatternDetector
from detection.risk_engine import RiskEngine
from detection.alert_engine import AlertEngine
from database.models import Customer, Account, Transaction, RiskHistory
from database.database import db
from datetime import datetime

class TransactionProcessor:
    def __init__(self, db_session=None):
        self.session = db_session or db.session
        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()
        self.ontology_reasoner = OntologyReasoner()
        self.risk_engine = RiskEngine()

    def process_transaction(self, transaction, commit=True):
        """
        Executes end-to-end detection pipeline on a single transaction.
        Updates transaction risk score, suspicious flag, alerts, and customer risk profiles.
        """
        # Fetch related DB objects
        sender_acc = self.session.query(Account).filter_by(account_number=transaction.sender_account).first()
        receiver_acc = self.session.query(Account).filter_by(account_number=transaction.receiver_account).first()

        sender_cust = self.session.query(Customer).filter_by(customer_id=sender_acc.customer_id).first() if sender_acc else None
        receiver_cust = self.session.query(Customer).filter_by(customer_id=receiver_acc.customer_id).first() if receiver_acc else None

        # Fetch recent transactions for context
        recent_txs = self.session.query(Transaction).filter(
            (Transaction.sender_account == transaction.sender_account) |
            (Transaction.receiver_account == transaction.sender_account)
        ).order_by(Transaction.transaction_date.desc()).limit(50).all()

        # 1. Rule Engine
        rule_evals = self.rule_engine.evaluate_all(
            transaction, sender_acc, receiver_acc, sender_cust, receiver_cust, recent_txs
        )

        # 2. ML Anomaly Detection
        ml_evals = self.anomaly_detector.detect(
            transaction, sender_acc, receiver_acc, recent_txs
        )

        # 3. Ontology Reasoning
        ontology_evals = self.ontology_reasoner.evaluate_transaction(
            transaction, sender_acc, receiver_acc, sender_cust, receiver_cust, recent_txs
        )

        # 4. Pattern Detection
        patterns = PatternDetector.detect_patterns(rule_evals, ontology_evals, ml_evals['anomaly_score'])

        # 5. Risk Scoring
        risk_result = self.risk_engine.calculate_risk(rule_evals, ontology_evals, ml_evals)

        # Update transaction record
        transaction.risk_score = risk_result['risk_score']
        transaction.risk_level = risk_result['risk_level']
        transaction.suspicious = risk_result['is_suspicious']
        if patterns:
            transaction.description = f"{patterns[0]['pattern_type']} ({patterns[0]['description']})"

        # 6. Generate Alert if suspicious
        alert = None
        if sender_cust and (risk_result['is_suspicious'] or patterns):
            alert = AlertEngine.generate_alert_if_needed(
                transaction, sender_cust.customer_id, risk_result, patterns, ontology_evals
            )

        # 7. Update Customer Risk Profile
        if sender_cust:
            self._update_customer_risk(sender_cust, risk_result)

        if commit:
            self.session.commit()

        return {
            'transaction_id': transaction.transaction_id,
            'risk_score': risk_result['risk_score'],
            'risk_level': risk_result['risk_level'],
            'suspicious': risk_result['is_suspicious'],
            'rule_results': rule_evals,
            'ontology_results': ontology_evals,
            'ml_results': ml_evals,
            'patterns': patterns,
            'reasons': risk_result['reasons'],
            'alert_generated': alert.alert_id if alert else None
        }

    def _update_customer_risk(self, customer, risk_result):
        """Recalculates customer risk level based on latest transaction."""
        new_score = round((customer.risk_score * 0.7) + (risk_result['risk_score'] * 0.3), 1)
        customer.risk_score = new_score

        if new_score <= 30:
            customer.risk_level = 'Low'
        elif new_score <= 70:
            customer.risk_level = 'Medium'
        else:
            customer.risk_level = 'High'

        # Record risk history
        rh = RiskHistory(
            customer_id=customer.customer_id,
            risk_score=new_score,
            risk_level=customer.risk_level,
            reason=f"Transaction evaluated with risk score {risk_result['risk_score']} ({risk_result['risk_level']}).",
            timestamp=datetime.utcnow()
        )
        self.session.add(rh)
