from os import environ, urandom
from sys import modules

import pymysql
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

modules["MySQLdb"] = pymysql

# init DB and migration
db_user = environ.get('MYSQL_USER')
db_password = environ.get('MYSQL_PASSWORD')
db_name = environ.get('MYSQL_DATABASE')
db_host = environ.get('MYSQL_SERVER')
if not db_host or not db_user or not db_password or not db_name:
    print('Missing connection environment variables')
    exit()

# load app constants
IS_DEBUG = environ.get('FLASK_ENV', 'production') == 'development'
ADMIN_USERNAME = environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD', 'secret')
APP_PORT = environ.get('FLASK_PORT', 5000)

app = Flask(__name__)
app.secret_key = urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = IS_DEBUG
auth = HTTPBasicAuth()
db = SQLAlchemy(app)