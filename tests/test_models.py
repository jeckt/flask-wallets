#!env/bin/python
# -*- encoding: utf-8 -*-

import sys
import os.path

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

import unittest
from app import db, models

class UserTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        u = models.User(username='steve', email='steve@email.com')
        u.hash_password('super-secret-password')
        db.session.add(u)
        db.session.commit()

        self.user = models.User.query.get(1)

    @classmethod
    def tearDownClass(self):
        for u in models.User.query.all():
            db.session.delete(u)

        db.session.commit()

    def test_user_has_username(self):
        assert self.user.username == 'steve'

    def test_user_has_email(self):
        assert self.user.email == 'steve@email.com'

    def test_verify_password_successful(self):
        assert self.user.verify_password('super-secret-password')

    def test_verify_password_unsuccessful(self):
        assert not self.user.verify_password('incorrect_password')

if __name__ == '__main__':
    unittest.main()

