import unittest
from app import create_app
from database.database import db
from database.models import User

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_login_page_renders(self):
        res = self.client.get('/login')
        self.assertEqual(res.status_code, 200)

    def test_authenticated_dashboard_redirect(self):
        # Unauthenticated access to dashboard should redirect to login
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 302)

    def test_login_success(self):
        res = self.client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

    def test_api_stats_endpoint(self):
        # Login first
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        res = self.client.get('/api/dashboard/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('total_transactions', data)
        self.assertIn('suspicious_transactions', data)

    def test_api_ontology_graph_endpoint(self):
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        res = self.client.get('/api/ontology/graph')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('nodes', data)
        self.assertIn('edges', data)

if __name__ == '__main__':
    unittest.main()
