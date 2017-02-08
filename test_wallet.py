"""
A set of tests for the wallet module
"""

import unittest

from wallet import Wallet, FundingTemplate

class WalletTestCases(unittest.TestCase):
    def test_create_valid_account(self):
        a = Wallet(50.0)

        self.assertAlmostEquals(a.balance(), 50.0)

    def test_create_account_int_balance(self):
        a = Wallet(50)

        self.assertEquals(type(a.balance()), float)
        self.assertAlmostEquals(a.balance(), 50.0)

    def test_invalid_opening_balance(self):
        with self.assertRaises(ValueError) as context:
            a = Wallet('x')

        msg = 'could not convert string to float: {}'.format('x')
        self.assertTrue(msg in context.exception)

class WalletAddTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.start_bal = 50.0
        self.a = Wallet(self.start_bal)

    def test_valid_add_to_account(self):
        add = 50.0
        self.a.add(add)

        new_bal = self.start_bal + add
        self.assertAlmostEquals(self.a.balance(), new_bal)

    def test_invalid_add_to_account(self):
        add = 'x'
        with self.assertRaises(ValueError) as context:
            self.a.add(add)

        msg = 'could not convert string to float: {}'.format(add)
        self.assertTrue(msg in context.exception)

if __name__ == '__main__':
    unittest.main()
