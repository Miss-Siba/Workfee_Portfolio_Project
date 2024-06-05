import unittest
from flask import Flask
from flask_testing import TestCase
import sys
from flask_sqlalchemy import SQLAlchemy
sys.path.append('..')
from app import app, db, User

class TestApp(unittest.TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        self.app = app.test_client()  # Create a test client
        self.app_context = app.app_context()  # Create an application context
        self.app_context.push()  # Push the context to activate it

        # Create all tables in the database
        db.create_all()

        # Add a test user to the database
        user = User(username='testuser', password='testpassword')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        # Drop the test database
        db.session.remove()
        db.drop_all()
        # Pop the application context to deactivate it
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Home Page', response.data)

    def test_login(self):
        response = self.client.post('/account', data=dict(
            login='login',
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in as: testuser', response.data)

    def test_signup(self):
        response = self.client.post('/account', data=dict(
            signup='signup',
            username='newuser',
            password='newpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have successfully registered!', response.data)

    def test_logout(self):
        self.client.post('/account', data=dict(
            login='login',
            username='testuser',
            password='testpassword'
        ), follow_redirects=True)
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

if __name__ == '__main__':
    unittest.main()

