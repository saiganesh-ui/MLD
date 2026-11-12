from datetime import datetime, timedelta
from config import Config

class RuleEngine:
    def __init__(self, config=None):
        self.config = config or Config

    def evaluate_all(self, transaction, sender_account, receiver_account, sender_customer, receiver_customer, recent_transactions=None):
        """
        Evaluates all 10 detection rules against a transaction and its context.
        Returns a dictionary of rule evaluations.
        """
        results = []
        recent_txs = recent_transactions or []

        # Rule 1: Large Transaction
        r1 = self.rule_large_transaction(transaction)
        results.append(r1)

        # Rule 2: High Transaction Frequency
        r2 = self.rule_transaction_frequency(transaction, recent_txs)
        results.append(r2)

        # Rule 3: Structuring / Smurfing
        r3 = self.rule_structuring_smurfing(transaction, recent_txs)
        results.append(r3)

        # Rule 4: Rapid Transfers
        r4 = self.rule_rapid_transfers(transaction, recent_txs)
        results.append(r4)

        # Rule 5: Circular Transactions
        r5 = self.rule_circular_transactions(transaction, recent_txs)
        results.append(r5)

        # Rule 6: Cross-Border Activity
        r6 = self.rule_cross_border_activity(transaction)
        results.append(r6)

        # Rule 7: High-Risk Geography
        r7 = self.rule_high_risk_geography(transaction)
        results.append(r7)

        # Rule 8: Multiple Senders to One Account (Aggregation)
        r8 = self.rule_multiple_senders_to_one(transaction, recent_txs)
        results.append(r8)

        # Rule 9: One Sender to Many Accounts (Dispersal)
        r9 = self.rule_one_sender_to_many(transaction, recent_txs)
        results.append(r9)

        # Rule 10: Dormant Account Activity
        r10 = self.rule_dormant_account_activity(transaction, recent_txs)
        results.append(r10)

        total_score_contribution = sum(r['score_contribution'] for r in results if r['detected'])

        return {
            'rules': results,
            'total_detected': sum(1 for r in results if r['detected']),
            'total_score_contribution': min(100.0, total_score_contribution)
        }

    def rule_large_transaction(self, tx):
        threshold = self.config.LARGE_TRANSACTION_THRESHOLD
        amount = float(tx.amount)
        detected = amount >= threshold
        return {
            'rule_id': 'RULE_1',
            'rule_name': 'Large Transaction Anomaly',
            'detected': detected,
            'score_contribution': 25.0 if detected else 0.0,
            'explanation': f'Transaction amount ${amount:,.2f} exceeds configured threshold of ${threshold:,.2f}.' if detected else 'Transaction amount is within normal parameters.',
            'evidence': {'amount': amount, 'threshold': threshold}
        }

    def rule_transaction_frequency(self, tx, recent_txs):
        window_hours = self.config.HIGH_FREQUENCY_WINDOW_HOURS
        threshold = self.config.HIGH_FREQUENCY_THRESHOLD
        cutoff = tx.transaction_date - timedelta(hours=window_hours)

        count = sum(1 for t in recent_txs if t.sender_account == tx.sender_account and t.transaction_date >= cutoff) + 1
        detected = count >= threshold

        return {
            'rule_id': 'RULE_2',
            'rule_name': 'High Transaction Frequency',
            'detected': detected,
            'score_contribution': 20.0 if detected else 0.0,
            'explanation': f'{count} transactions executed from account {tx.sender_account} within {window_hours} hours (Threshold: {threshold}).' if detected else 'Transaction frequency is normal.',
            'evidence': {'transaction_count': count, 'window_hours': window_hours}
        }

    def rule_structuring_smurfing(self, tx, recent_txs):
        min_amt = self.config.STRUCTURING_MIN_AMOUNT
        max_amt = self.config.STRUCTURING_MAX_AMOUNT
        amount = float(tx.amount)

        is_structuring_amt = min_amt <= amount <= max_amt
        # Count matching recent transactions
        cutoff = tx.transaction_date - timedelta(hours=24)
        similar_txs = [t for t in recent_txs if t.sender_account == tx.sender_account and min_amt <= float(t.amount) <= max_amt and t.transaction_date >= cutoff]

        detected = is_structuring_amt and (len(similar_txs) >= 1)

        return {
            'rule_id': 'RULE_3',
            'rule_name': 'Structuring / Smurfing Pattern',
            'detected': detected,
            'score_contribution': 25.0 if detected else (10.0 if is_structuring_amt else 0.0),
            'explanation': f'Multiple transactions identified just below mandatory reporting threshold (${min_amt:,.0f}–${max_amt:,.0f}).' if detected else 'No structuring pattern detected.',
            'evidence': {'amount': amount, 'recent_similar_count': len(similar_txs)}
        }

    def rule_rapid_transfers(self, tx, recent_txs):
        window_hours = self.config.RAPID_TRANSFER_WINDOW_HOURS
        cutoff = tx.transaction_date - timedelta(hours=window_hours)

        # Check if sender account received funds within window right before sending
        inflow = [t for t in recent_txs if t.receiver_account == tx.sender_account and t.transaction_date >= cutoff]
        detected = len(inflow) > 0 and float(tx.amount) >= 0.7 * sum(float(t.amount) for t in inflow)

        return {
            'rule_id': 'RULE_4',
            'rule_name': 'Rapid Pass-Through Transfer',
            'detected': detected,
            'score_contribution': 20.0 if detected else 0.0,
            'explanation': f'Account {tx.sender_account} received ${sum(float(t.amount) for t in inflow):,.2f} and rapidly transferred out ${float(tx.amount):,.2f} within {window_hours} hours.' if detected else 'No rapid transfer chain detected.',
            'evidence': {'inflow_count': len(inflow), 'window_hours': window_hours}
        }

    def rule_circular_transactions(self, tx, recent_txs):
        cutoff = tx.transaction_date - timedelta(hours=48)
        # Check if funds moved A -> B -> ... -> A
        detected = False
        chain = [tx.sender_account, tx.receiver_account]

        for prev in recent_txs:
            if prev.transaction_date >= cutoff:
                if prev.sender_account == tx.receiver_account and prev.receiver_account == tx.sender_account:
                    detected = True
                    chain.append(prev.sender_account)
                    break

        return {
            'rule_id': 'RULE_5',
            'rule_name': 'Circular Transaction Loop',
            'detected': detected,
            'score_contribution': 25.0 if detected else 0.0,
            'explanation': f'Reciprocal or circular transfer pattern identified between accounts {tx.sender_account} and {tx.receiver_account}.' if detected else 'No circular pattern detected.',
            'evidence': {'circular_chain': chain}
        }

    def rule_cross_border_activity(self, tx):
        detected = tx.sender_country.strip().lower() != tx.receiver_country.strip().lower()
        return {
            'rule_id': 'RULE_6',
            'rule_name': 'Cross-Border Transfer',
            'detected': detected,
            'score_contribution': 15.0 if detected else 0.0,
            'explanation': f'International fund transfer from {tx.sender_country} to {tx.receiver_country}.' if detected else 'Domestic transfer.',
            'evidence': {'sender_country': tx.sender_country, 'receiver_country': tx.receiver_country}
        }

    def rule_high_risk_geography(self, tx):
        high_risk = [c.lower() for c in self.config.HIGH_RISK_COUNTRIES]
        s_risk = tx.sender_country.strip().lower() in high_risk
        r_risk = tx.receiver_country.strip().lower() in high_risk

        detected = s_risk or r_risk
        flagged_countries = []
        if s_risk: flagged_countries.append(tx.sender_country)
        if r_risk: flagged_countries.append(tx.receiver_country)

        return {
            'rule_id': 'RULE_7',
            'rule_name': 'High-Risk Jurisdiction Involvement',
            'detected': detected,
            'score_contribution': 20.0 if detected else 0.0,
            'explanation': f'Transaction involves high-risk jurisdiction(s): {", ".join(flagged_countries)}.' if detected else 'Standard country jurisdiction.',
            'evidence': {'high_risk_countries_involved': flagged_countries}
        }

    def rule_multiple_senders_to_one(self, tx, recent_txs):
        cutoff = tx.transaction_date - timedelta(hours=24)
        senders = set(t.sender_account for t in recent_txs if t.receiver_account == tx.receiver_account and t.transaction_date >= cutoff)
        senders.add(tx.sender_account)

        detected = len(senders) >= 4
        return {
            'rule_id': 'RULE_8',
            'rule_name': 'Multiple Senders to Single Account (Fan-In Aggregation)',
            'detected': detected,
            'score_contribution': 15.0 if detected else 0.0,
            'explanation': f'Receiver account {tx.receiver_account} gathered funds from {len(senders)} distinct senders within 24 hours.' if detected else 'Normal receiver activity.',
            'evidence': {'unique_senders_count': len(senders)}
        }

    def rule_one_sender_to_many(self, tx, recent_txs):
        cutoff = tx.transaction_date - timedelta(hours=24)
        receivers = set(t.receiver_account for t in recent_txs if t.sender_account == tx.sender_account and t.transaction_date >= cutoff)
        receivers.add(tx.receiver_account)

        detected = len(receivers) >= 4
        return {
            'rule_id': 'RULE_9',
            'rule_name': 'Single Sender to Multiple Accounts (Fan-Out Dispersal)',
            'detected': detected,
            'score_contribution': 15.0 if detected else 0.0,
            'explanation': f'Sender account {tx.sender_account} dispersed funds to {len(receivers)} distinct receivers within 24 hours.' if detected else 'Normal sender activity.',
            'evidence': {'unique_receivers_count': len(receivers)}
        }

    def rule_dormant_account_activity(self, tx, recent_txs):
        dormant_days = self.config.DORMANT_DAYS_THRESHOLD
        sender_txs = [t for t in recent_txs if t.sender_account == tx.sender_account or t.receiver_account == tx.sender_account]

        if not sender_txs:
            # First transaction or long break
            detected = float(tx.amount) >= 15000.0
        else:
            last_tx_date = max(t.transaction_date for t in sender_txs)
            days_inactive = (tx.transaction_date - last_tx_date).days
            detected = days_inactive >= dormant_days and float(tx.amount) >= 15000.0

        return {
            'rule_id': 'RULE_10',
            'rule_name': 'Dormant Account Sudden Spike',
            'detected': detected,
            'score_contribution': 20.0 if detected else 0.0,
            'explanation': f'Sudden high-value transaction (${float(tx.amount):,.2f}) executed on an account after extended inactivity.' if detected else 'Regular account activity.',
            'evidence': {'amount': float(tx.amount)}
        }
