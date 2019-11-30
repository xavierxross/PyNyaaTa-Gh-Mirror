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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = urandom(24).hex()
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
