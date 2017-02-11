"""
collections.py
"""

import os
import shutil
import csv

from wallet import Wallet, FundingTemplate

class Collection(object):
    def __init__(self):
        self._i = 0
        self._n = 0

        self._items = {}

    def __iter__(self):
        self._i = 0
        self._n = len(self._items)
        return self

    def next(self):
        if self._i < self._n:
            i = self._i
            self._i += 1
            return self._items.keys()[i]
        else:
            raise StopIteration()

    def balance(self):
        return sum([x.balance() for x in self._items.values()])

    def __len__(self):
        return len(self._items)

    def __delitem__(self, key):
        del self._items[key]

    def __getitem__(self, key):
        if key not in self._items:
            msg = 'collection does not contain key {}.'.format(key)
            raise Exception(msg)

        return self._items[key]

    def create_item(self, key, value):
        if key in self._items:
            msg = 'Item {} already exists'.format(key)
            raise Exception(msg)

        self._items[key] = value

        self.save()

    def _load_collection_data(self):
        """loads data into a dictionary object"""

        if not os.path.isfile(self._data):
            raise IOError('No such file: {}'.format(self._data))

        try:
            with open(self._data, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    self._items[row[0]] = Wallet(float(row[1]))
        except Exception as e:
            raise e

    def save(self):
        """saves collection data to a csv"""
        if not os.path.isfile(self._data):
            raise IOError('No such file: {}'.format(self._data))

        try:
            with open(self._data, 'wb') as f:
                writer = csv.writer(f)
                for (k, v) in self._items.iteritems():
                    writer.writerow([k, v.balance()])
        except Exception as e:
            raise e

class Accounts(Collection):
    def __init__(self, conn):
        super(Accounts, self).__init__()

        self._data = os.path.join(conn, 'accounts.csv')
        self._load_collection_data()

    def __getitem__(self, key):
        if key not in self._items:
            msg = 'Accounts does not contain account {}.'.format(key)
            raise Exception(msg)

        return self._items[key]

class Wallets(Collection):
    def __init__(self, conn):
        super(Wallets, self).__init__()

        self._data = os.path.join(conn, 'wallets.csv')
        self._load_collection_data()

    def __getitem__(self, key):
        if key not in self._items:
            msg = 'Wallets does not contain wallet {}.'.format(key)
            raise Exception(msg)

        return self._items[key]

class FundingTemplates(Collection):
    def __init__(self, conn):
        super(FundingTemplates, self).__init__()

        self._data = os.path.join(conn, 'funding.csv')
        self._load_collection_data()

    def __getitem__(self, key):
        if key not in self._items:
            msg = 'Funding templates does not contain {}.'.format(key)
            raise Exception(msg)

        return self._items[key]

    def __setitem__(self, key, value):
        if key not in self._items:
            msg = 'Funding templates does not contain {}'.format(key)
            raise Exception(msg)

        self._items[key] = value

    def _load_collection_data(self):
        if not os.path.isfile(self._data):
            raise IOError('No such file: {}'.format(self._data))

        try:
            with open(self._data, 'rb') as f:
                reader = csv.reader(f)
                for row in reader:
                    template = row[0]
                    if template not in self._items:
                        amount = row[1]
                        frequency = row[2]
                        account = row[3]
                        self._items[template] = FundingTemplate(template,
                                amount, account, frequency)

                    self._items[template].add_wallet_to_allocation(row[4],
                            float(row[5]))
        except Exception as e:
            raise e

        for (k, v) in self._items.iteritems():
            if not v.valid():
                raise Exception("Invalid template: {}".format(v))

    def save(self):
        if not os.path.isfile(self._data):
            raise IOError('No such file: {}'.format(self._data))

        try:
            with open(self._data, 'wb') as f:
                writer = csv.writer(f)
                for (name, template) in self._items.iteritems():
                    for (wallet, amount) in template.allocation().iteritems():
                        writer.writerow([name, template.amount(),
                            template.frequency(), template.account(),
                            wallet, amount])
        except Exception as e:
            raise e
