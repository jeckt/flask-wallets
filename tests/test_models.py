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
        u = models.User(nickname='steve', email='steve@email.com')
        db.session.add(u)
        db.session.commit()

    @classmethod
    def tearDownClass(self):
        for u in models.User.query.all():
            db.session.delete(u)

        db.session.commit()

    def test_user_has_nickname(self):
        u = models.User.query.get(1)
        assert u.nickname == 'steve'

    def test_user_has_email(self):
        u = models.User.query.get(1)
        assert u.email == 'steve@email.com'

if __name__ == '__main__':
    unittest.main()

