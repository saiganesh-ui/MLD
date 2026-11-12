class PatternDetector:
    """
    Detects complex multi-step graph & sequence patterns across transaction streams:
    - Structuring / Smurfing
    - Layering
    - Circular Loops
    - Rapid Pass-through
    """

    @staticmethod
    def detect_patterns(rule_results, ontology_results, ml_anomaly_score):
        patterns = []

        # Extract detected rules
        rule_ids = [r['rule_id'] for r in rule_results.get('rules', []) if r['detected']]

        if 'RULE_3' in rule_ids or 'SmurfingPattern' in str(ontology_results.get('inferences', [])):
            patterns.append({
                'pattern_type': 'Smurfing / Structuring',
                'severity': 'HIGH',
                'description': 'Multiple transactions deliberately routed under mandatory threshold limits.'
            })

        if 'RULE_4' in rule_ids or 'RULE_8' in rule_ids or 'RULE_9' in rule_ids:
            patterns.append({
                'pattern_type': 'Layering / Rapid Pass-Through',
                'severity': 'HIGH',
                'description': 'Rapid movement of funds through intermediate accounts to obfuscate source trail.'
            })

        if 'RULE_5' in rule_ids or 'CircularTransactionPattern' in str(ontology_results.get('inferences', [])):
            patterns.append({
                'pattern_type': 'Circular Laundering Loop',
                'severity': 'CRITICAL',
                'description': 'Closed-loop transfer chain returning funds back to originating account.'
            })

        if 'RULE_7' in rule_ids and 'RULE_1' in rule_ids:
            patterns.append({
                'pattern_type': 'High-Value Offshore Transfer',
                'severity': 'HIGH',
                'description': 'Large transaction executed directly to or from a high-risk jurisdiction.'
            })

        if ml_anomaly_score >= 70 and not patterns:
            patterns.append({
                'pattern_type': 'Statistical Anomaly',
                'severity': 'MEDIUM',
                'description': 'Transaction parameters significantly deviate from standard behavior distributions.'
            })

        return patterns
