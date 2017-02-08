"""
A set of test for the wallets app module
"""

import unittest

import os

from app import App
import utils

class AppLoginTestCases(unittest.TestCase):
    def setUp(self):
        self.temp_path = utils.create_test_data()

    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_login_valid_account(self):
        user = 'steve'
        w = App(user, conn=self.temp_path)

    def test_login_account_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            user = 'john'
            w = App(user)

        msg = 'User {} does not exist'.format(user)
        self.assertTrue(msg in context.exception)

    def test_create_valid_user(self):
        user = 'mary'
        App.create_user(user, conn=self.temp_path)

        path = os.path.join(self.temp_path, user)
        self.assertTrue(os.path.isdir(path))
        files = ['accounts.csv','wallets.csv','funding.csv']
        for f in files:
            f = os.path.join(path, f)
            self.assertTrue(os.path.isfile(f))

    def test_create_existing_user(self):
        user = 'steve'
        with self.assertRaises(Exception) as context:
            App.create_user(user, conn=utils.TEST_USER_DATA_PATH)

        msg = 'User already exists: {}'.format(user)
        self.assertTrue(msg in context.exception)

    def test_remove_valid_user(self):
        user = 'steve'
        App.remove_user(user, conn=self.temp_path)

        self.assertFalse(os.path.isdir(os.path.join(self.temp_path, user)))

    def test_remove_non_existent_user(self):
        user = 'doug'
        with self.assertRaises(Exception) as context:
            App.remove_user(user, conn=self.temp_path)

        msg = 'User does not exist: {}'.format(user)
        self.assertTrue(msg in context.exception)

class AppTransferFundsTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_valid_account_transfer(self):
        accounts = self.app.accounts
        self.assertAlmostEquals(accounts['bank account'].balance(), 2475.0)
        self.assertAlmostEquals(accounts['cash'].balance(), 325.0)

        self.app.transfer_funds(225.0, from_acct='bank account',
                to_acct='cash', transfer_type='account')

        self.assertAlmostEquals(accounts['bank account'].balance(), 2250.0)
        self.assertAlmostEquals(accounts['cash'].balance(), 550.0)

    def test_insufficient_funds_for_account_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(350.0, from_acct='cash',
                    to_acct='bank account', transfer_type='account')

        msg = '{} has insufficient funds to transfer {}'.format('cash', 350.0)
        self.assertTrue(msg in context.exception)

    def test_invalid_to_account_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(250.0, from_acct='bank account',
                    to_acct='credit card', transfer_type='account')

        msg = 'To account does not exist: {}'.format('credit card')
        self.assertTrue(msg in context.exception)

    def test_invalid_from_account_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(10.0, from_acct='credit card',
                    to_acct='cash', transfer_type='account')

        msg = 'From account does not exist: {}'.format('credit card')
        self.assertTrue(msg in context.exception)

    def test_incorrect_amount_type_transfer(self):
        with self.assertRaises(ValueError) as context:
            self.app.transfer_funds('x', from_acct='bank account',
                    to_acct='cash', transfer_type='account')

        msg = 'could not convert string to float: {}'.format('x')
        self.assertTrue(msg in context.exception)

    def test_invalid_transfer_type(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(20, from_acct='savings',
                    to_acct='shares', transfer_type='fake')

        msg = 'Invalid transfer type: {}'.format('fake')
        self.assertTrue(msg in context.exception)

    def test_valid_wallet_transfer(self):
        wallets = self.app.wallets
        self.assertAlmostEquals(wallets['savings'].balance(), 350.0)
        self.assertAlmostEquals(wallets['shares'].balance(), 2350.0)

        self.app.transfer_funds(225.0, from_acct='savings',
                to_acct='shares', transfer_type='wallet')

        self.assertAlmostEquals(wallets['savings'].balance(), 125.0)
        self.assertAlmostEquals(wallets['shares'].balance(), 2575.0)

    def test_insufficient_funds_for_account_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(1350.0, from_acct='savings',
                    to_acct='shares', transfer_type='wallet')

        msg = '{} has insufficient funds to transfer {}'.format('savings', 1350.0)
        self.assertTrue(msg in context.exception)

    def test_invalid_to_wallet_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(250.0, from_acct='savings',
                    to_acct='fake', transfer_type='wallet')

        msg = 'To wallet does not exist: {}'.format('fake')
        self.assertTrue(msg in context.exception)

    def test_invalid_from_wallet_transfer(self):
        with self.assertRaises(Exception) as context:
            self.app.transfer_funds(10.0, from_acct='fake',
                    to_acct='savings', transfer_type='wallet')

        msg = 'From wallet does not exist: {}'.format('fake')
        self.assertTrue(msg in context.exception)

class AppRemoveWalletTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)
        self.wallets = self.app.wallets

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_remove_non_existent_wallet(self):
        wallet = 'bonds'
        transfer_acct = 'savings'
        with self.assertRaises(Exception) as context:
            self.app.remove_wallet(wallet, transfer=transfer_acct)

        msg = 'Wallet does not exist. {}'.format(wallet)
        self.assertTrue(msg in context.exception)

    def test_remove_existing_wallet(self):
        wallet = 'shares'
        transfer_acct = 'savings'
        add = self.app.wallets[wallet].balance()
        new_bal = self.app.wallets[transfer_acct].balance() + add

        funding = self.app.funding_templates['salary']
        alloc = funding.allocation()
        new_alloc_amount = alloc[wallet] + alloc[transfer_acct]

        self.app.remove_wallet(wallet, transfer=transfer_acct)

        self.assertTrue(wallet not in self.app.wallets)
        self.assertAlmostEquals(self.app.wallets[transfer_acct].balance(),
                new_bal)

        new_alloc = funding.allocation()
        self.assertTrue(wallet not in new_alloc)
        self.assertAlmostEquals(new_alloc[transfer_acct], new_alloc_amount)

    def test_remove_non_existent_transfer_wallet(self):
        wallet = 'shares'
        transfer_acct = 'bonds'
        with self.assertRaises(Exception) as context:
            self.app.remove_wallet(wallet, transfer=transfer_acct)

        msg = 'Transfer wallet does not exist. {}'.format(transfer_acct)
        self.assertTrue(msg in context.exception)

class AppRemoveAccountTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_remove_non_existent_account(self):
        account = 'free money'
        transfer = 'bank account'
        with self.assertRaises(Exception) as context:
            self.app.remove_account(account, transfer=transfer)

        msg = 'Account does not exist. {}'.format(account)
        self.assertTrue(msg in context.exception)

    def test_remove_existing_account(self):
        account = 'cash'
        transfer = 'bank account'
        add = self.app.accounts[account].balance()
        new_bal = self.app.accounts[transfer].balance() + add

        self.app.remove_account(account, transfer=transfer)

        self.assertTrue(account not in self.app.accounts)
        self.assertAlmostEquals(self.app.accounts[transfer].balance(),
                new_bal)

        funding = self.app.funding_templates['salary']
        self.assertEquals(transfer, funding.account())
        self.assertNotEquals(account, funding.account())

    def test_remove_non_existent_transfer_account(self):
        account = 'cash'
        transfer = 'investment'
        with self.assertRaises(Exception) as context:
            self.app.remove_account(account, transfer=transfer)

        msg = 'Transfer account does not exist. {}'.format(transfer)
        self.assertTrue(msg in context.exception)

class AppNewAccountTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)
        self.wallets = self.app.wallets

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_create_new_account(self):
        self.app.create_account('joint account', 0.0)

        self.assertEquals(len(self.app.accounts), 3)
        self.assertAlmostEquals(self.app.accounts['joint account'].balance(), 0.0)

    def test_create_existing_account(self):
        with self.assertRaises(Exception) as context:
            self.app.create_account('cash', 0.0)

        msg = 'Item {} already exists'.format('cash')
        self.assertTrue(msg in context.exception)

    def test_create_new_account_persists_in_data_storage(self):
        self.app.create_account('joint account', 100.0)

        self.assertEquals(len(self.app.accounts), 3)

        new_app = App('steve', conn=self.temp_path)
        self.assertEquals(len(new_app.accounts), 3)
        self.assertEquals(new_app.accounts['joint account'].balance(), 100.0)

    def test_create_new_wallet_incorrect_opening_balance(self):
        with self.assertRaises(ValueError) as context:
            self.app.create_wallet('joint account', 'not an integer')

        msg = 'could not convert string to float: {}'.format('not an integer')
        self.assertTrue(msg in context.exception)

class AppNewWalletTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)
        self.wallets = self.app.wallets

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_create_new_wallet(self):
        self.app.create_wallet('mortgage', 0.0)

        self.assertEquals(len(self.wallets), 4)
        self.assertAlmostEquals(self.wallets['mortgage'].balance(), 0.0)

    def test_create_existing_wallet(self):
        with self.assertRaises(Exception) as context:
            self.app.create_wallet('mobile', 0.0)

        msg = 'Item {} already exists'.format('mobile')
        self.assertTrue(msg in context.exception)

    def test_create_new_wallet_persists_in_data_storage(self):
        self.app.create_wallet('mortgage', 0.0)

        self.assertEquals(len(self.app.wallets), 4)

        new_app = App('steve', conn=self.temp_path)
        self.assertEquals(len(new_app.wallets), 4)
        self.assertEquals(new_app.wallets['mortgage'].balance(), 0.0)

    def test_create_new_wallet_incorrect_opening_balance(self):
        with self.assertRaises(ValueError) as context:
            self.app.create_wallet('mortgage', 'not an integer')

        msg = 'could not convert string to float: {}'.format('not an integer')
        self.assertTrue(msg in context.exception)

class AppAddExpenseTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_add_expense_to_valid_wallet(self):
        wallet_bal = self.app.wallets['mobile'].balance() - 50.0
        acc_bal = self.app.accounts['cash'].balance() - 50.0
        self.app.add_expense('mobile', 'cash', 50.0)

        self.assertAlmostEquals(self.app.wallets['mobile'].balance(),
                wallet_bal)
        self.assertAlmostEquals(self.app.accounts['cash'].balance(),
                acc_bal)

    def test_add_expense_to_invalid_wallet(self):
        with self.assertRaises(Exception) as context:
            self.app.add_expense('captain', 'cash', 50.0)

        msg = 'Wallet does not exist. {}'.format('captain')
        self.assertTrue(msg in context.exception)

    def test_add_expense_to_invalid_account(self):
        with self.assertRaises(Exception) as context:
            self.app.add_expense('mobile', 'people', 50.0)

        msg = 'Account does not exist. {}'.format('people')
        self.assertTrue(msg in context.exception)

    def test_add_expense_to_wallet_incorrect_type(self):
        with self.assertRaises(ValueError) as context:
            self.app.add_expense('mobile', 'cash', 'x')

        msg = 'could not convert string to float: x'
        self.assertTrue(msg in context.exception)

class AppAddFundingTemplateTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.template = 'wife'
        self.frequency = 'Monthly'
        self.amount = 1000.0
        self.account = 'bank account'
        self.allocation = {
                'mobile': 200.0,
                'savings': 250.0,
                'shares': 550.0
                }

    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.user = 'steve'
        self.app = App(self.user, conn=self.temp_path)

    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_loaded_existing_funding_templates(self):
        self.assertEquals(len(self.app.funding_templates), 1)

    def test_create_new_funding_template(self):
        self.app.create_funding_template(self.template, self.amount,
                self.account, self.frequency, self.allocation)

        self.assertEquals(len(self.app.funding_templates), 2)
        self.assertTrue(self.template in self.app.funding_templates)

    def test_fund_wallets(self):
        template = 'salary'

        self.assertTrue(template in self.app.funding_templates)
        funding = self.app.funding_templates[template]

        # check income amount is correct
        self.assertAlmostEquals(funding.amount(), 3000.0)

        # check before account balance
        account = funding.account()
        account_balance = 2475.0
        self.assertAlmostEquals(self.app.accounts[account].balance(), account_balance)

        # store balance after funding
        wallets = {}
        for (k, v) in funding.allocation().iteritems():
            wallets[k] = self.app.wallets[k].balance() + v
            account_balance += v

        self.app.fund_wallets(template)

        # check balances after funding. Check that it persist
        # to data storage as well.
        new_app = App(self.user, self.temp_path)
        self.assertAlmostEquals(new_app.accounts[account].balance(), account_balance)

        for (k, v) in wallets.iteritems():
            self.assertAlmostEquals(new_app.wallets[k].balance(), v)

    def test_use_invalid_funding_template(self):
        with self.assertRaises(Exception) as context:
            template = 'fake_tempalte'
            self.app.fund_wallets(template)

        msg = 'Funding does not contain template {}.'.format(template)
        self.assertTrue(msg in context.exception)

    def test_create_existing_funding_template(self):
        template = 'salary'
        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(template, self.amount,
                    self.account, self.frequency, self.allocation)

        msg = 'Funding template {} already exists'.format(template)
        self.assertTrue(msg in context.exception)

    def test_create_funding_template_incorrect_allocation(self):
        allocation = {
                'mobile': 100.0,
                'savings': 250.0,
                'shares': 550.0
                }

        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(self.template, self.amount,
                    self.account, self.frequency, allocation)

        msg = 'Allocation amount != funding amount'
        self.assertTrue(msg in context.exception)

    def test_create_funding_template_account_does_not_exist(self):
        account = "fake account"

        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(self.template, self.amount,
                    account, self.frequency, self.allocation)

        msg = 'Account {} does not exist'.format(account)
        self.assertTrue(msg in context.exception)

    def test_create_funding_template_wallet_does_not_exist(self): 
        allocation = {
                'fake wallet': 200.0,
                'savings': 250.0,
                'shares': 550.0
                }

        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(self.template, self.amount,
                    self.account, self.frequency, allocation)

        msg = 'Wallet {} does not exist'.format('fake wallet')
        self.assertTrue(msg in context.exception)

    def test_create_funding_template_incorrect_funding_value(self):
        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(self.template, 'string',
                    self.account, self.frequency, self.allocation)

        msg = 'could not convert string to float: {}'.format('string')
        self.assertTrue(msg in context.exception)

    def test_create_funding_template_incorrect_wallet_amount(self):
        allocation = {
                'mobile': 'string',
                'savings': 250.0,
                'shares': 550.0
                }

        with self.assertRaises(Exception) as context:
            self.app.create_funding_template(self.template, self.amount,
                    self.account, self.frequency, allocation)

        msg = 'could not convert string to float: {}'.format('string')
        self.assertTrue(msg in context.exception)

class AppRemoveFundingTemplateTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_remove_valid_funding_template(self):
        template = 'salary'
        self.app.remove_funding_template(template)
        self.assertEqual(len(self.app.funding_templates), 0)
        self.assertTrue(template not in self.app.funding_templates)

    def test_remove_invalid_funding_template(self):
        template = 'free money'
        with self.assertRaises(Exception) as context:
            self.app.remove_funding_template(template)

        msg = 'Funding template does not exist. {}'.format(template)
        self.assertTrue(msg in context.exception)
        self.assertEqual(len(self.app.funding_templates), 1)

# NOTE(steve): Update template methods share the same
# base of methods as creating a new funding template
# thus don't need to add large test coverage for
# update funding templates.
class AppUpdateFundingTemplateTestCases(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.temp_path = utils.create_test_data()

        self.app = App('steve', conn=self.temp_path)

        self.template = 'salary'
        self.funding = self.app.funding_templates[self.template]

    @classmethod
    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_update_valid_account(self):
        account = 'cash'
        self.assertEquals(self.funding.account(), 'bank account')

        self.funding.update_account(account)
        self.assertEquals(self.funding.account(), account)

    def test_update_invalid_template(self):
        with self.assertRaises(Exception) as context:
            self.template = 'fake template'
            self.app.update_funding_template(self.template,
                    self.funding.amount(),
                    self.funding.account(),
                    self.funding.frequency(),
                    self.funding.allocation())

        msg = 'Funding template does not exist: {}'.format(self.template)
        self.assertTrue(msg in context.exception)

    def test_update_funding_template(self):
        amount = 4000.0
        new_alloc = self.funding.allocation()
        new_alloc['shares'] = new_alloc['shares'] + 1000.0
        self.app.update_funding_template(self.template,
                amount,
                self.funding.account(),
                self.funding.frequency(),
                new_alloc)

        self.funding = self.app.funding_templates[self.template]
        self.assertAlmostEquals(self.funding.amount(), 4000.0)
        update_alloc = self.funding.allocation()
        self.assertAlmostEquals(update_alloc['savings'], 1250.0)
        self.assertAlmostEquals(update_alloc['shares'], 2750.0)

if __name__ == '__main__':
    unittest.main()
