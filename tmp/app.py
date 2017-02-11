"""
app.py
"""

import os
import shutil

from wallets import Wallets, Accounts, FundingTemplates
from wallet import FundingTemplate, Wallet

class App(object):
    def __init__(self, user, conn=None):
        self.conn = user
        if conn:
            self.conn = os.path.join(conn, user)

        if not os.path.isdir(self.conn):
            msg = 'User {} does not exist'.format(user)
            raise Exception(msg)

        self.wallets = Wallets(self.conn)
        self.accounts = Accounts(self.conn)
        self.funding_templates = FundingTemplates(self.conn)

    #TODO(steve): make this more pythonic
    # by removing them from the class
    @staticmethod
    def create_user(user, conn=None):
        data = user
        if conn:
            data = os.path.join(conn, user)

        if os.path.isdir(data):
            raise Exception('User already exists: {}'.format(user))

        os.mkdir(data)
        files = ['accounts.csv','wallets.csv','funding.csv']
        for f in files:
            f = os.path.join(data, f)
            open(f, 'wb').close()

    @staticmethod
    def remove_user(user, conn=None):
        data = user
        if conn:
            data = os.path.join(conn, user)

        if not os.path.isdir(data):
            msg = 'User does not exist: {}'.format(user)
            raise Exception(msg)

        shutil.rmtree(data)

    # TODO(steve): should we check that wallet is of
    # type string?? Could have unwanted behaviour
    # if not.
    def create_wallet(self, wallet, opening_balance):
        try:
            valid_balance = float(opening_balance)
        except ValueError as e:
            raise e

        self.wallets.create_item(wallet, Wallet(valid_balance))

    def create_account(self, account, opening_balance):
        try:
            valid_balance = float(opening_balance)
        except ValueError as e:
            raise e

        self.accounts.create_item(account, Wallet(valid_balance))

    def create_funding_template(self, template, amount, account,
            frequency, allocation):

        if template in self.funding_templates:
            msg = 'Funding template {} already exists'.format(template)
            raise Exception(msg)

        funding_template = self._create_funding_template(template, amount,
                account, frequency, allocation)
        self.funding_templates.create_item(template, funding_template)

    def _create_funding_template(self, template, amount, account,
            frequency, allocation):

        if account not in self.accounts:
            msg = 'Account {} does not exist'.format(account)
            raise Exception(msg)

        try:
            funding_template = FundingTemplate(template, amount,
                    account, frequency)
        except Exception as e:
            raise e

        for (k, v) in allocation.iteritems():
            if k not in self.wallets:
                msg = 'Wallet {} does not exist'.format(k)
                raise Exception(msg)

            funding_template.add_wallet_to_allocation(k, v)

        if not funding_template.valid():
            msg = 'Allocation amount != funding amount'
            raise Exception(msg)

        return funding_template

    def remove_wallet(self, wallet, transfer):
        if wallet not in self.wallets:
            msg = 'Wallet does not exist. {}'.format(wallet)
            raise Exception(msg)

        if transfer not in self.wallets:
            msg = 'Transfer wallet does not exist. {}'.format(transfer)
            raise Exception(msg)

        bal = self.wallets[wallet].balance()
        self.wallets[transfer].add(bal)
        del self.wallets[wallet]

        for f in self.funding_templates:
            self.funding_templates[f].remove_wallet_from_allocation(wallet,
                    transfer=transfer)

    def remove_account(self, account, transfer):
        if account not in self.accounts:
            msg = 'Account does not exist. {}'.format(account)
            raise Exception(msg)

        if transfer not in self.accounts:
            msg = 'Transfer account does not exist. {}'.format(transfer)
            raise Exception(msg)

        bal = self.accounts[account].balance()
        self.accounts[transfer].add(bal)
        del self.accounts[account]

        for f in self.funding_templates:
            if self.funding_templates[f].account() == account:
                self.funding_templates[f].update_account(transfer)

    def remove_funding_template(self, template):
        if template not in self.funding_templates:
            msg = 'Funding template does not exist. {}'.format(template)
            raise Exception(msg)

        del self.funding_templates[template]

    def update_funding_template(self, template, amount, account,
            frequency, allocation):

        if template not in self.funding_templates:
            msg = 'Funding template does not exist: {}'.format(template)
            raise Exception(msg)

        try:
            funding_template = self._create_funding_template(template, amount,
                    account, frequency, allocation)
        except Exception as e:
            raise e

        self.funding_templates[template] = funding_template

    def add_expense(self, wallet, account, amount):
        if wallet not in self.wallets:
            msg = 'Wallet does not exist. {}'.format(wallet)
            raise Exception(msg)

        if account not in self.accounts:
            msg = 'Account does not exist. {}'.format(account)
            raise Exception(msg)

        try:
            valid_amount = float(amount)
        except ValueError as e:
            raise e

        self.wallets[wallet].add(-valid_amount)
        self.accounts[account].add(-valid_amount)

    def transfer_funds(self, amount, from_acct, to_acct, transfer_type):
        try:
            valid_amount = float(amount)
        except ValueError as e:
            raise e

        collection = None
        if transfer_type == 'account':
            collection = self.accounts
        elif transfer_type =='wallet':
            collection = self.wallets
        else:
            msg = 'Invalid transfer type: {}'.format(transfer_type)
            raise Exception(msg)

        if from_acct not in collection:
            msg = 'From {} does not exist: {}'.format(transfer_type, from_acct)
            raise Exception(msg)

        if to_acct not in collection:
            msg = 'To {} does not exist: {}'.format(transfer_type, to_acct)
            raise Exception(msg)

        if collection[from_acct].balance() < valid_amount:
            msg = '{} has insufficient funds to transfer {}'.format(from_acct,
                    amount)
            raise Exception(msg)

        collection[from_acct].add(-valid_amount)
        collection[to_acct].add(valid_amount)

    def fund_wallets(self, template):
        if template not in self.funding_templates:
            msg = 'Funding does not contain template {}.'.format(template)
            raise Exception(msg)

        funding = self.funding_templates[template]
        self.accounts[funding.account()].add(funding.amount())
        for (k, v) in funding.allocation().iteritems():
            self.wallets[k].add(v)

        self.accounts.save()
        self.wallets.save()
