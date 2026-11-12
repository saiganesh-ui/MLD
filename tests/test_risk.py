import unittest
from detection.risk_engine import RiskEngine

class TestRiskEngine(unittest.TestCase):
    def setUp(self):
        self.risk_engine = RiskEngine()

    def test_risk_score_calculation(self):
        rule_evals = {
            'rules': [
                {'rule_id': 'RULE_1', 'detected': True, 'score_contribution': 25.0, 'explanation': 'Large Tx'},
                {'rule_id': 'RULE_7', 'detected': True, 'score_contribution': 20.0, 'explanation': 'High Risk Geo'}
            ],
            'total_score_contribution': 45.0
        }
        ontology_evals = {'is_suspicious': True, 'inferences': ['HighRiskCountry']}
        ml_evals = {'is_anomaly': True, 'anomaly_score': 80.0}

        result = self.risk_engine.calculate_risk(rule_evals, ontology_evals, ml_evals)

        self.assertGreaterEqual(result['risk_score'], 50.0)
        self.assertIn(result['risk_level'], ['Medium', 'High'])
        self.assertGreater(len(result['reasons']), 0)

    def test_low_risk_calculation(self):
        rule_evals = {'rules': [], 'total_score_contribution': 0.0}
        ontology_evals = {'is_suspicious': False, 'inferences': []}
        ml_evals = {'is_anomaly': False, 'anomaly_score': 10.0}

        result = self.risk_engine.calculate_risk(rule_evals, ontology_evals, ml_evals)

        self.assertLessEqual(result['risk_score'], 30.0)
        self.assertEqual(result['risk_level'], 'Low')

if __name__ == '__main__':
    unittest.main()
