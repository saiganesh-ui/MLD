import unittest
from app import create_app
from database.database import db
from database.models import User, Customer, Account, Transaction
from config import Config
import json

class TestUIRedesignEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Perform login for authenticated routes
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})

    def test_page_1_ontology_explorer_renders(self):
        res = self.client.get('/ontology')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Ontology & Knowledge Graph Explorer', res.data)
        self.assertIn(b'mynetwork', res.data)

    def test_page_1_classes_api(self):
        res = self.client.get('/api/ontology/classes')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('classes', data)
        class_names = [c['name'] for c in data['classes']]
        self.assertIn('Customer', class_names)
        self.assertIn('Account', class_names)
        self.assertIn('Transaction', class_names)
        self.assertIn('SuspiciousTransaction', class_names)
        self.assertIn('NormalTransaction', class_names)
        self.assertIn('Alert', class_names)
        self.assertIn('RiskLevel', class_names)
        self.assertIn('LowRisk', class_names)
        self.assertIn('MediumRisk', class_names)
        self.assertIn('HighRisk', class_names)
        self.assertIn('Country', class_names)
        self.assertIn('HighRiskCountry', class_names)
        self.assertIn('TransactionPattern', class_names)
        self.assertIn('SmurfingPattern', class_names)
        self.assertIn('LayeringPattern', class_names)
        self.assertIn('CircularTransactionPattern', class_names)
        self.assertIn('RapidTransferPattern', class_names)
        self.assertIn('CrossBorderPattern', class_names)
        self.assertIn('ShellEntity', class_names)

    def test_page_1_graph_api_with_entity_filter(self):
        res = self.client.get('/api/ontology/graph?limit=20&entity_type=Customer')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('nodes', data)
        self.assertIn('edges', data)

    def test_page_2_sar_reports_renders(self):
        res = self.client.get('/reports')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Automated Regulatory Reports', res.data)
        self.assertIn(b'System Summary & SAR Report', res.data)

    def test_page_2_pdf_generation(self):
        res = self.client.get('/reports/download/pdf/system-summary')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Content-Type'), 'application/pdf')

    def test_page_2_csv_exports(self):
        res_tx = self.client.get('/reports/download/csv/transactions')
        self.assertEqual(res_tx.status_code, 200)
        self.assertEqual(res_tx.headers.get('Content-Type'), 'text/csv')

        res_al = self.client.get('/reports/download/csv/alerts')
        self.assertEqual(res_al.status_code, 200)
        self.assertEqual(res_al.headers.get('Content-Type'), 'text/csv')

    def test_page_3_data_ingestion_renders(self):
        res = self.client.get('/import')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Batch Data Import Pipeline', res.data)
        self.assertIn(b'EXECUTE IMPORT & DETECTION PIPELINE', res.data)
        self.assertIn(b'pipeline-stage-container', res.data)

    def test_page_4_engine_tuning_renders(self):
        res = self.client.get('/settings')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Detection Engine & Weight Configuration', res.data)
        self.assertIn(b'Risk Engine Weights', res.data)
        self.assertIn(b'Rule Engine Thresholds', res.data)

    def test_page_4_settings_api_get_and_post(self):
        # GET settings
        res = self.client.get('/api/settings')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('weights', data)
        self.assertIn('thresholds', data)

        # POST valid settings
        new_weights = {
            'amount_anomaly': 30,
            'frequency_anomaly': 15,
            'transaction_pattern': 25,
            'geographic_factor': 15,
            'historical_behavior': 15
        }
        res_post = self.client.post('/api/settings', json={'weights': new_weights})
        self.assertEqual(res_post.status_code, 200)
        post_data = res_post.get_json()
        self.assertTrue(post_data['success'])
        self.assertEqual(Config.RISK_WEIGHTS['amount_anomaly'], 30)

        # Reset back
        default_weights = {
            'amount_anomaly': 25,
            'frequency_anomaly': 20,
            'transaction_pattern': 25,
            'geographic_factor': 15,
            'historical_behavior': 15
        }
        self.client.post('/api/settings', json={'weights': default_weights})

        # POST invalid settings (sum != 100)
        invalid_weights = {
            'amount_anomaly': 10,
            'frequency_anomaly': 10,
            'transaction_pattern': 10,
            'geographic_factor': 10,
            'historical_behavior': 10
        }
        res_invalid = self.client.post('/api/settings', json={'weights': invalid_weights})
        self.assertEqual(res_invalid.status_code, 400)

    def test_page_5_login_page_renders_split_screen(self):
        # Logout first
        self.client.get('/logout')
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'AML Analytics Portal', res.data)
        self.assertIn(b'login-split-container', res.data)
        self.assertIn(b'SIGN IN TO CONSOLE', res.data)

if __name__ == '__main__':
    unittest.main()
