from config import Config

class RiskEngine:
    def __init__(self, config=None):
        self.config = config or Config
        self.weights = self.config.RISK_WEIGHTS
        self.thresholds = self.config.RISK_THRESHOLDS

    def calculate_risk(self, rule_evaluations, ontology_evaluations, ml_evaluations, customer_historical_score=0.0):
        """
        Computes composite transparent risk score (0-100) and risk level with explicit score breakdown.
        """
        score = 0.0
        reasons = []

        rules = rule_evaluations.get('rules', [])
        rule_dict = {r['rule_id']: r for r in rules}

        # 1. Amount Anomaly Factor (0-25)
        if rule_dict.get('RULE_1', {}).get('detected'):
            addition = self.weights['amount_anomaly']
            score += addition
            reasons.append({'factor': 'Large Amount Anomaly', 'score': addition, 'text': rule_dict['RULE_1']['explanation']})
        elif rule_dict.get('RULE_3', {}).get('detected'):
            addition = 20.0
            score += addition
            reasons.append({'factor': 'Structuring Amount Anomaly', 'score': addition, 'text': 'Transaction amount structured under reporting threshold.'})

        # 2. Frequency Anomaly Factor (0-20)
        if rule_dict.get('RULE_2', {}).get('detected'):
            addition = self.weights['frequency_anomaly']
            score += addition
            reasons.append({'factor': 'High Transaction Frequency', 'score': addition, 'text': rule_dict['RULE_2']['explanation']})

        # 3. Transaction Pattern Factor (0-25)
        pattern_added = False
        if rule_dict.get('RULE_4', {}).get('detected'):
            score += 20.0
            reasons.append({'factor': 'Rapid Pass-Through Chain', 'score': 20.0, 'text': rule_dict['RULE_4']['explanation']})
            pattern_added = True

        if rule_dict.get('RULE_5', {}).get('detected'):
            score += 25.0
            reasons.append({'factor': 'Circular Transaction Loop', 'score': 25.0, 'text': rule_dict['RULE_5']['explanation']})
            pattern_added = True

        if ontology_evaluations.get('is_suspicious') and not pattern_added:
            score += 15.0
            reasons.append({'factor': 'Ontology Semantic Inference', 'score': 15.0, 'text': 'Matched semantic rules in MoneyLaunderingDetectionOntology.'})

        # 4. Geographic Factor (0-15)
        if rule_dict.get('RULE_7', {}).get('detected'):
            addition = self.weights['geographic_factor']
            score += addition
            reasons.append({'factor': 'High-Risk Jurisdiction', 'score': addition, 'text': rule_dict['RULE_7']['explanation']})
        elif rule_dict.get('RULE_6', {}).get('detected'):
            addition = 10.0
            score += addition
            reasons.append({'factor': 'Cross-Border Transfer', 'score': addition, 'text': rule_dict['RULE_6']['explanation']})

        # 5. Historical / ML Anomaly Factor (0-15)
        if ml_evaluations.get('is_anomaly'):
            ml_score = round(ml_evaluations['anomaly_score'] * (self.weights['historical_behavior'] / 100.0), 1)
            score += ml_score
            reasons.append({'factor': 'Isolation Forest ML Anomaly', 'score': ml_score, 'text': f'ML model flagged transaction as anomalous (Anomaly score: {ml_evaluations["anomaly_score"]}).'})

        # Cap at max 100
        final_score = min(100.0, round(score, 1))

        # Risk Level determination
        if final_score <= self.thresholds['low_max']:
            risk_level = 'Low'
        elif final_score <= self.thresholds['medium_max']:
            risk_level = 'Medium'
        else:
            risk_level = 'High'

        return {
            'risk_score': final_score,
            'risk_level': risk_level,
            'reasons': reasons,
            'is_suspicious': final_score >= self.thresholds['medium_max'] + 1,  # >= 71 is High Risk suspicious
            'detection_breakdown': {
                'rule_engine_score': rule_evaluations.get('total_score_contribution', 0.0),
                'ontology_inference': ontology_evaluations.get('is_suspicious', False),
                'ml_anomaly_score': ml_evaluations.get('anomaly_score', 0.0)
            }
        }
