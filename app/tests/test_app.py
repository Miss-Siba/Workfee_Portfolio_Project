import unittest
from flask import Flask
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask_testing import TestCase
import sys
import os
from flask_sqlalchemy import SQLAlchemy
from ..app import create_app, db



class TestApp(unittest.TestCase):

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user
        user = User(username='testuser', email='abc@cde.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        self.client = self.app.test_client()

    def tearDown(self):
        # Drop the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.post('/signup', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password',
            'password2': 'password'
        })
        self.assertEqual(response.status_code, 200)


    def test_logout(self):
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
