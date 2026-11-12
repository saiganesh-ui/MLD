from ml.predict import MLAnomalyPredictor

class AnomalyDetector:
    def __init__(self):
        self.predictor = MLAnomalyPredictor()

    def detect(self, transaction, sender_account=None, receiver_account=None, recent_transactions=None):
        amount = float(transaction.amount)
        recent_txs = recent_transactions or []
        frequency = len([t for t in recent_txs if t.sender_account == transaction.sender_account]) + 1
        cross_border = transaction.sender_country.strip().lower() != transaction.receiver_country.strip().lower()

        res = self.predictor.predict_anomaly(amount, frequency, cross_border)
        return {
            'anomaly_score': res['anomaly_score'],
            'normalized_anomaly_score': res['anomaly_score'],
            'is_anomaly': res['is_anomaly'],
            'anomaly_status': res['status'],
            'raw_score': res['raw_decision_score'],
            'detection_method': 'Isolation Forest ML Engine'
        }
