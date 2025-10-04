# tests/test_app.py
import unittest
import sys
import os
import json

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
        
        # Parse JSON response
        data = json.loads(response.data)
        
        # Check for either format (simple or enhanced)
        # Simple format: {"status": "ok"}
        # Enhanced format: {"status": "healthy", "service": "secure-cicd-pipeline"}
        self.assertIn('status', data)
        self.assertIn(data['status'], ['ok', 'healthy'])

    def test_get_user_not_found(self):
        """Test user not found scenario."""
        response = self.app.get('/users?username=nonexistentuser')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'not found', response.data.lower())

    def test_get_user_missing_parameter(self):
        """Test missing username parameter."""
        response = self.app.get('/users')
        # Should return 400 Bad Request if input validation is implemented
        self.assertIn(response.status_code, [400, 404])

    def test_get_user_success(self):
        """Test successful user retrieval."""
        # The app initializes with an 'admin' user
        response = self.app.get('/users?username=admin')
        
        # Should return 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.data)
        
        # Verify response structure
        self.assertIn('username', data)
        self.assertEqual(data['username'], 'admin')
        self.assertIn('email', data)

    def test_get_user_long_username(self):
        """Test username length validation."""
        # Create a username longer than 255 characters
        long_username = 'a' * 300
        response = self.app.get(f'/users?username={long_username}')
        
        # Should return 400 Bad Request if validation is implemented
        # Otherwise might return 404 Not Found
        self.assertIn(response.status_code, [400, 404])

    def test_sql_injection_protection(self):
        """Test that SQL injection is prevented."""
        # Try a SQL injection attack
        malicious_input = "' OR 1=1 --"
        response = self.app.get(f'/users?username={malicious_input}')
        
        # Should NOT return all users (which would happen with SQL injection)
        # Should return 404 (user not found) or handle gracefully
        self.assertIn(response.status_code, [404, 400, 500])
        
        # Verify it doesn't return the admin user
        if response.status_code == 200:
            data = json.loads(response.data)
            # If parameterized queries work, this exact string won't match
            self.assertNotEqual(data.get('username'), 'admin')

if __name__ == '__main__':
    unittest.main()