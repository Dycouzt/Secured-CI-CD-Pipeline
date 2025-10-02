# tests/test_app.py
import unittest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from app import app

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        """Set up a test client."""
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        """Test the health check endpoint."""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ok', response.data)

    def test_get_user_not_found(self):
        """Test user not found scenario."""
        response = self.app.get('/users?username=nonexistentuser')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'User not found', response.data)

if __name__ == '__main__':
    unittest.main()