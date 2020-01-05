from os import environ, urandom

from flask import Flask
from flask.cli import load_dotenv
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy

# init DB and migration
load_dotenv()
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
CACHE_TIMEOUT = environ.get('CACHE_TIMEOUT', 60 * 60)

app = Flask(__name__)
app.name = 'PyNyaaTa'
app.secret_key = urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (
    db_user, db_password, db_host, db_name
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_POOL_RECYCLE'] = 200
app.config['SQLALCHEMY_ECHO'] = IS_DEBUG
app.url_map.strict_slashes = False
auth = HTTPBasicAuth()
db = SQLAlchemy(app)
