import unittest
from app import create_app
from app.db import get_db

class SmallBadgeTestCase(unittest.TestCase):
    def setUp(self):
        """Sets up a test application client and ensures test mode configuration."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/smallbadge_test'
        self.client = self.app.test_client()
        
        # Clear testing database collections before each test runs
        with self.app.app_context():
            db = get_db()
            db.users.delete_many({})
            db.organizations.delete_many({})
            db.issued_badges.delete_many({})

    def tearDown(self):
        """Clean up database records after tests."""
        with self.app.app_context():
            db = get_db()
            db.users.delete_many({})
            db.organizations.delete_many({})
            db.issued_badges.delete_many({})

    def test_public_index_loads(self):
        """Verify that the public verify/lookup page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Verify a Badge', response.data)

    def test_register_org_get_loads(self):
        """Verify that organization registration forms are accessible."""
        response = self.client.get('/register-org')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register Organization', response.data)

    def test_unauthorized_admin_dashboard_redirects(self):
        """Ensure that access to admin dashboards redirect to login when unauthenticated."""
        response = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Please log in to access this page.', response.data)

if __name__ == '__main__':
    unittest.main()
