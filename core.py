from sys import modules
from flask import Flask
from os import environ
from flask_sqlalchemy import SQLAlchemy
import pymysql

modules["MySQLdb"] = pymysql
app = Flask(__name__)

# init DB and migration
db_user = environ.get('MYSQL_USER')
db_password = environ.get('MYSQL_PASSWORD')
db_name = environ.get('MYSQL_DATABASE')
db_host = environ.get('MYSQL_HOSTNAME')
if not db_host or not db_user or not db_password or not db_name:
    print('Missing connection environment variables')
    exit()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
