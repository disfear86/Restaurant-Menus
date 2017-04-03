import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/Database_name'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'dev-key'

OAUTH = {
        'facebook': {
            'id': '<facebook client id>',
            'secret': '<facebook client secret>'
            },
        'google': {
            'id': '<google client id>',
            'secret': '<google client secret>',
            }
        }
