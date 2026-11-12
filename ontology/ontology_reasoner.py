from ontology.ontology_rules import ONTOLOGY_RULES
from config import Config

class OntologyReasoner:
    """
    Ontology-based semantic reasoner that infers suspicious activity
    and enriches detection results with rule antecedents, inferences, and source facts.
    """
    def __init__(self, ontology_manager=None):
        self.manager = ontology_manager

    def evaluate_transaction(self, transaction, sender_account, receiver_account, sender_customer, receiver_customer, recent_transactions=None):
        """
        Evaluates a single transaction against ontology rules.
        Returns a dictionary of ontology reasoning results.
        """
        inferences = []
        rules_triggered = []
        source_facts = []

        amount = float(transaction.amount)
        sender_country = transaction.sender_country
        receiver_country = transaction.receiver_country
        high_risk_countries = Config.HIGH_RISK_COUNTRIES

        # Fact logging
        source_facts.append(f"Sender Account: {sender_account.account_number} ({sender_country})")
        source_facts.append(f"Receiver Account: {receiver_account.account_number} ({receiver_country})")
        source_facts.append(f"Transaction Amount: ${amount:,.2f}")

        # Rule 1: High-Risk Cross Border
        if (sender_country in high_risk_countries or receiver_country in high_risk_countries) and amount >= 10000:
            rules_triggered.append(ONTOLOGY_RULES[0])
            inferences.append("Classified as HighRiskCrossBorder due to jurisdiction risk matching ontology class HighRiskCountry.")

        # Rule 2: Structuring / Smurfing
        if Config.STRUCTURING_MIN_AMOUNT <= amount <= Config.STRUCTURING_MAX_AMOUNT:
            rules_triggered.append(ONTOLOGY_RULES[1])
            inferences.append(f"Classified as SmurfingPattern (Amount ${amount:,.2f} lies in structuring band $8,000–$9,999).")

        # Rule 3: Circular Transaction (if recent transactions provided)
        if recent_transactions:
            # Check if funds return to sender account in recent flow
            for prev_t in recent_transactions:
                if prev_t.sender_account == receiver_account.account_number and prev_t.receiver_account == sender_account.account_number:
                    rules_triggered.append(ONTOLOGY_RULES[2])
                    inferences.append("Classified as CircularTransactionPattern (Direct reciprocal transfer flow detected between accounts).")
                    break

        is_suspicious = len(inferences) > 0

        return {
            'is_suspicious': is_suspicious,
            'inferences': inferences,
            'rules_triggered': rules_triggered,
            'source_facts': source_facts,
            'disclaimer': 'Detected activity is classified as potentially suspicious based on semantic ontology rules for research review.'
        }
