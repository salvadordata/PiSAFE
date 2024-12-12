import unittest
from eas_alert import generate_alert

class TestEASAlert(unittest.TestCase):
    def test_generate_alert_success(self):
        alert = generate_alert(event_code='RWT', location='12345', duration=30)
        self.assertIsNotNone(alert)
        self.assertIn('EAS Alert', alert)

    def test_generate_alert_invalid_event_code(self):
        with self.assertRaises(ValueError):
            generate_alert(event_code='INVALID', location='12345', duration=30)

if __name__ == '__main__':
    unittest.main()