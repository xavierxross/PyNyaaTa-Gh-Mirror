from os import environ
from sys import modules

import pymysql
from flask import Flask
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix

modules["MySQLdb"] = pymysql

# init DB and migration
db_user = environ.get('MYSQL_USER')
db_password = environ.get('MYSQL_PASSWORD')
db_name = environ.get('MYSQL_DATABASE')
db_host = environ.get('MYSQL_HOST')
if not db_host or not db_user or not db_password or not db_name:
    print('Missing connection environment variables')
    exit()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (db_user, db_password, db_host, db_name)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
auth = HTTPBasicAuth()
db = SQLAlchemy(app)


@auth.verify_password
def verify_password(username, password):
    admin_username = environ.get('ADMIN_USERNAME', 'admin')
    admin_password = environ.get('ADMIN_USERNAME', 'secret')
    return username is admin_username and password is admin_password


@app.route('/')
def hello_world():
    return 'Hello World !'


if __name__ == '__main__':
    app_debug = environ.get('FLASK_ENV', 'production') is 'development'
    app.run('0.0.0.0', debug=app_debug)
