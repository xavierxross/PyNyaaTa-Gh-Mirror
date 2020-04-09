from os import environ, urandom

from flask import Flask
from flask.cli import load_dotenv
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

IS_DEBUG = environ.get('FLASK_ENV', 'production') == 'development'
ADMIN_USERNAME = environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD', 'secret')
APP_PORT = environ.get('FLASK_PORT', 5000)
CACHE_TIMEOUT = environ.get('CACHE_TIMEOUT', 60 * 60)
BLACKLIST_WORDS = environ.get('BLACKLIST_WORDS', '').split(',')
MYSQL_ENABLED = False

app = Flask(__name__)
app.name = 'PyNyaaTa'
app.secret_key = urandom(24).hex()
app.url_map.strict_slashes = False
auth = HTTPBasicAuth()

db_host = environ.get('MYSQL_SERVER')
if db_host:
    MYSQL_ENABLED = True
    db_user = environ.get('MYSQL_USER')
    db_password = environ.get('MYSQL_PASSWORD')
    db_name = environ.get('MYSQL_DATABASE')
    if not db_user or not db_password or not db_name:
        print('Missing connection environment variables')
        exit()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
        db_user, db_password, db_host, db_name
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ECHO'] = IS_DEBUG
    db = SQLAlchemy(app)