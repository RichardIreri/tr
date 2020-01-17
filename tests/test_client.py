""" Framework for testing using Flask test client. """

import re
import unittest
from app import create_app, db
from app.models import Role, User

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Home page test.
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    # Simulation of a new user workflow with the flask test client
    def test_register_and_login(self):
        # Register a new account
        response = self.client.post('/auth/register', data={
            'email': 'radioampex@gmail.com',
            'username': 'radio',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertEqual(response.status_code, 302)

        # Log in with the new account
        response = self.client.post('/auth/login', data={
            'email': 'radioampex@gmail.com',
            'password': 'cat'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('Hello,\s+radio',
                                    response.get_data(as_text=True)))
        self.assertTrue(
            'You have not confirmed your account yet' in response.get_data(
                as_text=True))

        # Send a confirmation token
        user = User.query.filter_by(email='radioampex@gmail.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get('/auth/confirm/{}'.format(token),
                                    follow_redirects=True)
        user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'You have confirmed your account' in response.get_data(
                as_text=True))

        # Log out 
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You have been logged out' in response.get_data(
            as_text=200))


