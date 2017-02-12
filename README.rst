======
README
======

Wallets is a web app that implements the envelope budgeting
system. It will be an app that follows the simple is better
principle.

The wallets app allows users to create accounts and wallets.
Accounts are real entities such as bank accounts, credit cards,
savings accounts, investments as shares etc. Wallets on the other
hand are the "envelopes" of the system. They are logical categories
they allow users to give a purpose to every dollar they earn.

Funding templates are meant to make it easy to allocate money
earned into the wallets.

=============
RELEASE NOTES
=============

0.0.1 (2017-02-08)
++++++++++++++++++

* Conception

====
TODO
====

#. (DONE) Create a git repo and load to GitHub.
#. (DONE) Restructure the app to use flask and database
#. (DONE) Create virtual environment to store dependencies
#. (DONE) Create test database framework for unit testing

    #. (DONE) Implement config.py to store database connections
    #. (DONE) Create unit test for creating a user
    #. (DONE) Build a small script to clean all database objects

#. Set up simple views to run the web app for manual functional testing

    #. (DONE) Simple hello world display using templates and jinja2
    #. (DONE) Create login/sign up form.
    #. (DONE) Create login/sign up view.
    #. Create a mock dashboard for logged in user

#. Implement wallet model and unit tests around creation of wallets and accounts
#. Implement functionality to fund wallets with accounts
#. Implement transaction model and unit tests around creation of transactions
#. Extend the wallet model with balance and expense reporting functionality
#. Implement transfers models which allows users to transfer funds between accounts and wallets but not between wallets and accounts.
#. Implement funding templates functionality to automate recurring funding of wallets from accounts e.g. funding wallets using salary.
#. Implement user authentication and registration of new users
#. Design web interface!!
