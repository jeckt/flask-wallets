#!env/bin/python
# -*- encoding: utf-8 -*-

import sys
import os.path

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

def create():
    from app import db

    db.create_all()
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO,
                            api.version(SQLALCHEMY_MIGRATE_REPO))

def migrate():
    import imp
    from app import db

    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    migration = SQLALCHEMY_MIGRATE_REPO + \
            ('/versions/%03d_migration.py' % (v+1))

    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DATABASE_URI,
                                 SQLALCHEMY_MIGRATE_REPO)
    exec(old_model, tmp_module.__dict__)

    script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI,
                                              SQLALCHEMY_MIGRATE_REPO,
                                              tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)

    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    print('New migration saved as {}'.format(migration))
    print('Current database version: {}'.format(str(v)))

def upgrade():
    api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    print('Current database version: {}'.format(str(v)))

def downgrade():
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)

    print('Current database version: {}'.format(str(v)))

if __name__ == '__main__':
    import argparse

    desc = """A set of database tools for building web apps using python
    and SQLAlchemy.
    """
    parser = argparse.ArgumentParser(description=desc)

    options = parser.add_mutually_exclusive_group()
    options.add_argument('--create', action="store_true",
                         help="Create a new db")
    options.add_argument('--migrate', action="store_true",
                         help="Migrate db with new changes")
    options.add_argument('--upgrade', action="store_true",
                         help="Upgrade db to newer version")
    options.add_argument('--downgrade', action="store_true",
                         help="Downgrade db to older version")

    args = parser.parse_args()

    if args.create:
        create()
    elif args.migrate:
        migrate()
    elif args.upgrade:
        upgrade()
    elif args.downgrade:
        downgrade()
    else:
        print("$ python db_tools.py --help")
