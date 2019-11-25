from core import app
from models import *
from flask import Response, request
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from os import environ


# init HTTP basic auth
def check_auth(username, password):
    # This function is called to check if a username / password combination is valid.
    admin_username = environ.get('ADMIN_USERNAME', 'admin')
    admin_password = environ.get('ADMIN_USERNAME', 'secret')
    return username == admin_username and password == admin_password


def authenticate():
    # Sends a 401 response that enables basic auth
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def hello_world():
    return 'Hello World !'
