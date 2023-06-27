import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'i-dont-know-her'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/flask_db"
    OAUTH_CREDENTIALS = {
        'vk': {
            'id': '',
            'secret': ''
        }
    }
