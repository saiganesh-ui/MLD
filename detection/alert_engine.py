import uuid
from datetime import datetime
from database.models import Alert, AuditLog
from database.database import db

class AlertEngine:
    """
    Automated Alert Generation Engine.
    Severity Levels: INFO, WARNING, HIGH, CRITICAL
    Statuses: Open, Under Review, Resolved, False Positive
    """
    @staticmethod
    def generate_alert_if_needed(transaction, customer_id, risk_result, patterns, ontology_results):
        score = risk_result['risk_score']

        if score < 40 and not risk_result['is_suspicious']:
            return None  # No alert required for standard low risk

        # Determine severity
        if score >= 85 or any(p['severity'] == 'CRITICAL' for p in patterns):
            severity = 'CRITICAL'
        elif score >= 70 or any(p['severity'] == 'HIGH' for p in patterns):
            severity = 'HIGH'
        elif score >= 50:
            severity = 'WARNING'
        else:
            severity = 'INFO'

        alert_type = patterns[0]['pattern_type'] if patterns else 'Elevated Risk Score'
        
        # Build evidence description
        evidence_lines = [f"Risk Score: {score}/100 ({risk_result['risk_level']})"]
        for r in risk_result.get('reasons', []):
            evidence_lines.append(f"• {r['factor']} (+{r['score']}): {r['text']}")
        
        if ontology_results.get('inferences'):
            evidence_lines.append("Ontology Inferences:")
            for inf in ontology_results['inferences']:
                evidence_lines.append(f"  - {inf}")

        description = "\n".join(evidence_lines)

        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"

        alert = Alert(
            alert_id=alert_id,
            transaction_id=transaction.transaction_id,
            customer_id=customer_id,
            alert_type=alert_type,
            severity=severity,
            description=description,
            risk_score=score,
            status='Open',
            created_at=datetime.utcnow()
        )

        db.session.add(alert)
        
        # Log audit entry
        audit = AuditLog(
            user='SYSTEM_DETECTION_ENGINE',
            action='ALERT_GENERATED',
            entity='Alert',
            entity_id=alert_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit)
        db.session.commit()

        return alert
