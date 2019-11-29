from os import environ

from flask import redirect, render_template, url_for

from config import app, auth
from models import SearchForm


@auth.verify_password
def verify_password(username, password):
    admin_username = environ.get('ADMIN_USERNAME', 'admin')
    admin_password = environ.get('ADMIN_USERNAME', 'secret')
    return username is admin_username and password is admin_password


@app.route('/')
def home():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search', q=form.q))
    return render_template('home.html', form=form)


@app.route('/search')
def search():
    return 'Hello!'


if __name__ == '__main__':
    app_debug = environ.get('FLASK_ENV', 'production') is 'development'
    app.run('0.0.0.0', debug=app_debug)
