import logging
from os import environ, urandom

from flask import Flask
from flask.cli import load_dotenv
from flask_apscheduler import APScheduler
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

IS_DEBUG = environ.get('FLASK_ENV', 'production') == 'development'
ADMIN_USERNAME = environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD', 'secret')
APP_PORT = int(environ.get('FLASK_PORT', 5000))
CACHE_TIMEOUT = int(environ.get('CACHE_TIMEOUT', 60 * 60))
REQUESTS_TIMEOUT = int(environ.get('REQUESTS_TIMEOUT', 5))
BLACKLIST_WORDS = environ.get('BLACKLIST_WORDS', '').split(',') if environ.get('BLACKLIST_WORDS', '') else []
CLOUDPROXY_ENDPOINT = environ.get('CLOUDPROXY_ENDPOINT')
MYSQL_ENABLED = False

app = Flask(__name__)
app.name = 'PyNyaaTa'
app.debug = IS_DEBUG
app.secret_key = urandom(24).hex()
app.url_map.strict_slashes = False
auth = HTTPBasicAuth()
scheduler = APScheduler(app=app)
logging.basicConfig(level=(logging.DEBUG if IS_DEBUG else logging.INFO))
logger = logging.getLogger(app.name)

db_host = environ.get('MYSQL_SERVER')
if db_host:
    MYSQL_ENABLED = True
    db_user = environ.get('MYSQL_USER')
    db_password = environ.get('MYSQL_PASSWORD')
    db_name = environ.get('MYSQL_DATABASE')
    if not db_user or not db_password or not db_name:
        logger.error('Missing connection environment variables')
        exit()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
        db_user, db_password, db_host, db_name
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 200
    }
    db = SQLAlchemy(app)
