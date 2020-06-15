"""
Contains the standard configuration settings for the Flask application.
Many settings are pulled from the execution environment, or defaulted if no data is found.
"""
import os
from dotenv import load_dotenv
from datetime import timedelta

# Attempts to load environmental variables from files in project directory.
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
# .flaskenv will include Flask specific environmental variables.
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'704c8e3be839417893f99b7bf1e60a26'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "app.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 25
    REMEMBER_COOKIE_DURATION = timedelta(days=2)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['tylor_branch@hotmail.com']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
