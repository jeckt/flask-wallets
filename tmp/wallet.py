"""
wallet.py
"""

class Wallet(object):
    def __init__(self, open_balance):
        try:
            self._balance = float(open_balance)
        except ValueError as e:
            raise e

    def balance(self):
        return self._balance

    def add(self, amount):
        try:
            self._balance += float(amount)
        except ValueError as e:
            raise e

class FundingTemplate(object):
    def __init__(self, template, amount, account, frequency):
        try:
            self._amount = float(amount)
        except ValueError as e:
            raise e

        self._template = template
        self._account = account
        self._frequency = frequency
        self._allocation = {}

    def add_wallet_to_allocation(self, wallet, amount):
        if wallet in self._allocation:
            msg = 'Wallet {} already exists in allocation'.format(wallet)
            raise Exception(msg)

        try:
            self._allocation[wallet] = float(amount)
        except ValueError as e:
            raise e

    def remove_wallet_from_allocation(self, wallet, transfer):
        if wallet not in self._allocation:
            msg = 'Wallet does not exist. {}'.format(wallet)
            raise Exception(msg)

        if transfer not in self._allocation:
            self._allocation[transfer] = float(0)

        amount = self._allocation[wallet]
        self._allocation[transfer] += float(amount)

        del self._allocation[wallet]

    def update_account(self, account):
        self._account = account

    def amount(self):
        return self._amount

    def account(self):
        return self._account

    def frequency(self):
        return self._frequency

    def allocation(self):
        return self._allocation.copy()

    def valid(self):
        """Check if the funding template is valid"""
        alloc_amount = sum([v for (k, v) in self._allocation.iteritems()])
        return (abs(alloc_amount - self._amount) < 1e-10)

