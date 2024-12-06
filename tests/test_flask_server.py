import unittest
from flask_server import app

class TestFlaskServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to PiSAFE', response.data)

    def test_alert_endpoint(self):
        response = self.client.post('/alert', json={
            'event_code': 'RWT',
            'location': '12345',
            'duration': 30
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Alert sent successfully', response.data)

    def test_invalid_route(self):
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()