"""
A set of tests for the wallets module
"""

import unittest

from app import App
import utils

class AccountsTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.temp_path = utils.create_test_data()
        self.app = App('steve', conn=self.temp_path)
        self.accounts = self.app.accounts

    @classmethod
    def tearDownClass(self):
        utils.remove_test_data(self.temp_path)

    def test_total_balance_on_all_accounts(self):
        self.assertAlmostEquals(self.accounts.balance(), 2800.0)

    def test_number_of_accounts(self):
        self.assertEquals(len(self.accounts), 2)

    def test_accounts_contains_a_account(self):
        self.assertTrue('cash' in self.accounts)

    def test_accounts_does_not_contain_a_account(self):
        self.assertTrue('credit card' not in self.accounts)

    def test_get_valid_account_in_accounts(self):
        self.assertAlmostEqual(self.accounts['cash'].balance(), 325.0)

    def test_get_invalid_account_in_accounts(self):
        with self.assertRaises(Exception) as context:
            self.accounts['credit card']

        msg = 'Accounts does not contain account {}.'.format('credit card')
        self.assertTrue(msg in context.exception)

class WalletsTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)
        self.wallets = self.app.wallets

    @classmethod
    def tearDownClass(self):
        utils.remove_test_data(self.temp_path)

    def test_total_balance_on_all_wallets(self):
        self.assertAlmostEquals(self.wallets.balance(), 2800.0)

    def test_number_of_wallets(self):
        self.assertEquals(len(self.wallets), 3)

    def test_wallets_contains_a_wallet(self):
        self.assertTrue('shares' in self.wallets)

    def test_wallets_does_not_contain_a_wallet(self):
        self.assertTrue('mortgage' not in self.wallets)

    def test_get_valid_wallet_in_wallets(self):
        self.assertAlmostEqual(self.wallets['mobile'].balance(), 100.0)

    def test_get_invalid_wallet_in_wallets(self):
        with self.assertRaises(Exception) as context:
            self.wallets['mortgage']

        msg = 'Wallets does not contain wallet {}.'.format('mortgage')
        self.assertTrue(msg in context.exception)

class FundingTemplateRemoveWalletTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)
        self.wallet = 'shares'
        self.transfer = 'savings'
        self.funding = self.app.funding_templates['salary']

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_remove_valid_wallet(self):
        alloc = self.funding.allocation()
        new_bal = alloc[self.transfer] + alloc[self.wallet]
        self.funding.remove_wallet_from_allocation(self.wallet,
                    transfer=self.transfer)

        new_alloc = self.funding.allocation()
        self.assertTrue(self.wallet not in new_alloc)
        self.assertAlmostEquals(new_alloc[self.transfer], new_bal)

    def test_remove_invalid_wallet(self):
        self.wallet = 'not a wallet'
        with self.assertRaises(Exception) as context:
            self.funding.remove_wallet_from_allocation(self.wallet,
                    transfer=self.transfer)

        msg = 'Wallet does not exist. {}'.format(self.wallet)
        self.assertTrue(msg in context.exception)

    def test_remove_wallet_new_transfer_wallet_in_allocation(self):
        self.transfer = 'mobile'
        alloc = self.funding.allocation()
        bal = alloc[self.wallet]
        self.funding.remove_wallet_from_allocation(self.wallet,
                    transfer=self.transfer)

        new_alloc = self.funding.allocation()
        self.assertTrue(self.wallet not in new_alloc)
        self.assertTrue(self.transfer in new_alloc)
        self.assertAlmostEquals(new_alloc[self.transfer], bal)

if __name__ == '__main__':
    unittest.main()
