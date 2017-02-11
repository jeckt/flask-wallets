"""
encoding: -*- utf-8 -*-

A set of functional tests on a prototype of
envelope budgeting

"""

import unittest

import os

from app import App
import utils

class NewUserFunctionalTests(unittest.TestCase):
    def setUp(self):
        self.temp_path = utils.create_test_data()

    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_create_new_user(self):
        # Steve tells Mary about this new
        # fantastic app and Mary decides to
        # use it. She begins by creating
        # a new user
        user = 'Mary'
        App.create_user(user, conn=self.temp_path)
        app = App(user, conn=self.temp_path)

        # Mary checks that no accounts, wallets, 
        # or funding templates have been set up.
        self.assertEquals(len(app.wallets), 0)
        self.assertEquals(len(app.accounts), 0)
        self.assertEquals(len(app.funding_templates), 0)

        # Mary starts by adding her accounts
        app.create_account('cash', 125.0)
        app.create_account('transaction', 2055.0)
        app.create_account('online savings', 20000.0)
        self.assertEquals(len(app.accounts), 3)
        self.assertAlmostEquals(app.accounts.balance(), 22180.0)
        self.assertAlmostEquals(app.accounts['cash'].balance(), 125.0)
        self.assertAlmostEquals(app.accounts['transaction'].balance(), 2055.0)
        self.assertAlmostEquals(app.accounts['online savings'].balance(), 20000.0)

        # Mary then creates a set of wallets to
        # allocate her funds to.
        app.create_wallet('mobile', 180.0)
        app.create_wallet('mortgage', 10000.0)
        app.create_wallet('holiday', 2000.0)
        app.create_wallet('investments', 10000.0)
        self.assertEquals(len(app.wallets), 4)
        self.assertAlmostEquals(app.wallets.balance(), 22180.0)
        self.assertAlmostEquals(app.wallets['mobile'].balance(), 180.0)
        self.assertAlmostEquals(app.wallets['mortgage'].balance(), 10000.0)
        self.assertAlmostEquals(app.wallets['holiday'].balance(), 2000.0)
        self.assertAlmostEquals(app.wallets['investments'].balance(), 10000.0)

        # Lastly Mary adds a funding template for
        # the salary she earns.
        template = 'salary'
        amount = 2500.0
        frequency = 'Monthly'
        account = 'transaction'
        allocation = {
                'mobile': 50.0,
                'mortgage': 1500.0,
                'investments': 950.0
                }

        app.create_funding_template(template, amount, account, frequency,
                allocation)
        self.assertTrue(template in app.funding_templates)

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        self.temp_path = utils.create_test_data()
        self.user = 'steve'
        self.app = App(self.user, conn=self.temp_path)

    def tearDown(self):
        utils.remove_test_data(self.temp_path)

    def test_current_balances_on_wallets(self):
        # Steve can see that there are three
        # wallets in his account
        self.assertEquals(len(self.app.wallets), 3)

        # Steve then wants to know the 
        # current balances in each wallet
        self.assertAlmostEquals(self.app.wallets['mobile'].balance(), 100.0)
        self.assertAlmostEquals(self.app.wallets['savings'].balance(), 350.0)
        self.assertAlmostEquals(self.app.wallets['shares'].balance(), 2350.0)

        # Steve then checks the total balance
        self.assertAlmostEquals(self.app.wallets.balance(), 2800.0)

    def test_current_balances_on_accounts_steve(self):
        # Steve then proceeds to check that
        # he indeeds has two accounts
        self.assertEquals(len(self.app.accounts), 2)

        # Steve then wants to know the
        # current balances in each account
        self.assertEquals(self.app.accounts['cash'].balance(), 325.0)
        self.assertEquals(self.app.accounts['bank account'].balance(), 2475.0)

        # Steve then checks the total balance
        # on all accounts
        self.assertAlmostEquals(self.app.accounts.balance(), 2800.0)

    def test_create_an_account(self):
        # Steve checks that he has two accounts
        self.assertEquals(len(self.app.accounts), 2)

        # He decides to open another account with 
        # his wife so that they can both deposit
        # their salary into it. They deposit 100.0
        # into the account to open it
        self.app.create_account('joint account', 100.0)

        # He then checks to ensure that the account 
        self.assertEquals(len(self.app.accounts), 3)
        self.assertTrue('joint account' in self.app.accounts)

        # The next day Steve opens up the app
        # and checks the balance in his joint account
        # to see if his wife added any money!
        new_app = App(self.user, self.temp_path)
        self.assertAlmostEquals(new_app.accounts['joint account'].balance(), 100.0)

    def test_create_wallet_in_account(self):
        # He checks that he has three wallets
        self.assertEquals(len(self.app.wallets), 3)

        # After purchasing a property for him
        # and his wife he decides to open a
        # new wallet to pay the mortgage expense
        # from with an opening balance of zero.
        self.app.create_wallet('mortgage', 0.0)

        # He checks that the wallet has indeed
        # been added
        self.assertEquals(len(self.app.wallets), 4)

        # The next day Steve opens up the app
        # to check what the balance is in
        # his new wallet
        new_app = App(self.user, self.temp_path)
        self.assertAlmostEquals(new_app.wallets['mortgage'].balance(), 0.0)

    def test_create_and_use_funding_template(self):
        # After setting up his accounts and 
        # wallets. Steve is ready to create
        # his first funding template to allocate
        # his wife's monthly salary.
        template = 'wife'
        amount = 1000.0
        frequency = 'Monthly'
        account = 'bank account'
        allocation = {
                'mobile': 100.0,
                'savings': 400.0,
                'shares': 500.0
                }

        self.app.create_funding_template(template, amount, account, frequency,
                allocation)

        # The next day Steve gets paid and 1000.0 appears
        # in his bank account. He opens up the app
        # to update this
        self.app.fund_wallets(template)

        # He then proceeds to check that his account has 
        # been appropriately updated.
        self.assertAlmostEquals(self.app.accounts[account].balance(), 3475.0)

        # He then checks to ensure that his wallets have been
        # topped up correctly as well
        self.assertAlmostEquals(self.app.wallets['mobile'].balance(), 200.0)
        self.assertAlmostEquals(self.app.wallets['savings'].balance(), 750.0)
        self.assertAlmostEquals(self.app.wallets['shares'].balance(), 2850.0)

    def test_pay_credit_card(self):
        # It is the dreaded time of the month
        # Steve logs into App and adds
        # a credit card account
        self.app.create_account('credit card', -250.0)
        self.assertEquals(len(self.app.accounts), 3)
        self.assertAlmostEquals(self.app.accounts['credit card'].balance(),
                -250.0)

        # He then proceeds to pay off his credit card
        # with his bank funds
        self.app.transfer_funds(250.0, from_acct='bank account',
                to_acct='credit card', transfer_type='account')

        # He then checks that the transaction completed
        # successfully
        self.assertAlmostEquals(self.app.accounts['bank account'].balance(), 2225.0)
        self.assertAlmostEquals(self.app.accounts['credit card'].balance(), 0.0)

    def test_invest_savings_into_shares(self):
        # Steve has saved up quite a bit of money
        # over the last few months and decides
        # now is a good time to invest those
        # funds into shares.
        self.app.transfer_funds(200, from_acct='savings',
                to_acct='shares', transfer_type='wallet')

        # He then checks that the transfer was
        # successful.
        self.assertAlmostEquals(self.app.wallets['savings'].balance(), 150.0)
        self.assertAlmostEquals(self.app.wallets['shares'].balance(), 2550.0)

    def test_update_funding_template(self):
        # Steve recently got promoted as his job and
        # thus needs to update his funding template
        # to reflect this
        self.assertTrue('salary' in self.app.funding_templates)
        funding = self.app.funding_templates['salary']

        # he updates his allocation
        new_alloc = funding.allocation()
        new_alloc['savings'] = new_alloc['savings'] + 1000.0

        # he updates the funding template
        new_funding = self.app.update_funding_template('salary',
                4000.0, funding.account(), funding.frequency(),
                new_alloc)

        # He then checks that his new funding template has
        # been update correctly with his new income
        # and allocations
        fd = self.app.funding_templates['salary']
        self.assertAlmostEquals(fd.amount(), 4000.0)
        self.assertAlmostEquals(fd.allocation()['savings'], 2250.0)
        self.assertAlmostEquals(fd.allocation()['shares'], 1750.0)

    def test_remove_account(self):
        # Steve logs into the wallets app
        # and checks that he has two accounts
        self.assertEquals(len(self.app.accounts), 2)
        self.assertAlmostEquals(self.app.accounts['cash'].balance(), 325.0)
        self.assertAlmostEquals(self.app.accounts['bank account'].balance(), 2475.0)

        # Steve wants to close his bank account
        # and revert back to the cash economy! cash
        # only baby! He has got his employer to agree
        # to pay him cash
        self.app.remove_account('bank account', transfer='cash')
        self.assertEquals(len(self.app.accounts), 1)
        self.assertAlmostEquals(self.app.accounts['cash'].balance(), 2800.0)

        # He then checks to ensure that his
        # funding templates have been updated
        # for this change
        funding = self.app.funding_templates['salary']
        self.assertNotEquals('bank account', funding.account())
        self.assertEquals('cash', funding.account())

    def test_remove_wallet(self):
        # Steve logs into the wallets app
        # and checks that he has three wallets
        self.assertEquals(len(self.app.wallets), 3)
        self.assertAlmostEquals(self.app.wallets['savings'].balance(), 350.0)
        self.assertAlmostEquals(self.app.wallets['shares'].balance(), 2350.0)

        # Steve wants to sell all his shares
        # and not invest in them anymore.
        # He decides to transfer the
        # remaining balance to savings
        self.app.remove_wallet('shares',transfer='savings')
        self.assertEquals(len(self.app.wallets), 2)
        self.assertAlmostEquals(self.app.wallets['savings'].balance(), 2700.0)

        # He then checks to ensure that his
        # funding templates have been
        # updated for this change.
        funding = self.app.funding_templates['salary']
        self.assertTrue('shares' not in funding.allocation())
        self.assertAlmostEquals(funding.allocation()['savings'], 3000.0)

    def test_remove_funding_template(self):
        # Steve logs into the wallets app
        # and checks that he still has
        # one funding template
        self.assertEquals(len(self.app.funding_templates), 1)
        self.assertTrue('salary' in self.app.funding_templates)

        # Steve recently got made redundant and in
        # agony decided to delete his funding template
        self.app.remove_funding_template('salary')

        # He then checks that this is successful
        self.assertEquals(len(self.app.funding_templates), 0)
        self.assertTrue('salary' not in self.app.funding_templates)

    def test_add_expense_to_wallets(self):
        # Steve logs into the wallets app
        # and checks his mobile wallet balance
        self.assertAlmostEquals(self.app.accounts['cash'].balance(), 325.0)
        self.assertAlmostEquals(self.app.wallets['mobile'].balance(), 100.0)

        # He proceeds to pay his mobile bill with cash
        self.app.add_expense('mobile', 'cash', 50.0)

        # He then checks that his balance and account
        # have been correctly adjusted
        self.assertAlmostEquals(self.app.accounts['cash'].balance(), 275.0)
        self.assertAlmostEquals(self.app.wallets['mobile'].balance(), 50.0)

if __name__ == '__main__':
    unittest.main()
