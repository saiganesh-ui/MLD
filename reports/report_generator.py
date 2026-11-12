from database.models import Customer, Account, Transaction, Alert
from database.database import db

class ReportGenerator:
    def __init__(self, db_session=None):
        self.session = db_session or db.session

    def get_system_summary_data(self):
        total_customers = self.session.query(Customer).count()
        total_accounts = self.session.query(Account).count()
        total_transactions = self.session.query(Transaction).count()
        suspicious_count = self.session.query(Transaction).filter_by(suspicious=True).count()
        open_alerts = self.session.query(Alert).filter_by(status='Open').count()
        high_risk_customers = self.session.query(Customer).filter_by(risk_level='High').count()

        all_scores = [t.risk_score for t in self.session.query(Transaction.risk_score).all()]
        avg_risk_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        stats = {
            'total_customers': total_customers,
            'total_accounts': total_accounts,
            'total_transactions': total_transactions,
            'suspicious_count': suspicious_count,
            'open_alerts': open_alerts,
            'high_risk_customers': high_risk_customers,
            'avg_risk_score': round(avg_risk_score, 1)
        }

        recent_txs = self.session.query(Transaction).order_by(Transaction.transaction_date.desc()).limit(20).all()
        alerts = self.session.query(Alert).order_by(Alert.risk_score.desc()).limit(20).all()

        return stats, recent_txs, alerts
