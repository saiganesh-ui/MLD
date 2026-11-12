import csv
import io

class CSVExporter:
    @staticmethod
    def export_transactions(transactions):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Transaction ID', 'Sender Account', 'Receiver Account', 'Amount',
            'Currency', 'Type', 'Date', 'Sender Country', 'Receiver Country',
            'Risk Score', 'Risk Level', 'Suspicious'
        ])

        for t in transactions:
            writer.writerow([
                t.transaction_id, t.sender_account, t.receiver_account, f"{t.amount:.2f}",
                t.currency, t.transaction_type, t.transaction_date, t.sender_country,
                t.receiver_country, t.risk_score, t.risk_level, 'YES' if t.suspicious else 'NO'
            ])
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def export_alerts(alerts):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Alert ID', 'Transaction ID', 'Customer ID', 'Alert Type',
            'Severity', 'Risk Score', 'Status', 'Created At'
        ])

        for a in alerts:
            writer.writerow([
                a.alert_id, a.transaction_id, a.customer_id, a.alert_type,
                a.severity, a.risk_score, a.status, a.created_at
            ])
        output.seek(0)
        return output.getvalue()
