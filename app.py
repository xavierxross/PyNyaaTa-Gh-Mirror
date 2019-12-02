from operator import itemgetter
from os import environ

from flask import redirect, render_template, url_for, request

from config import app, auth
from connectors import *
from models import SearchForm, AnimeTitle


@auth.verify_password
def verify_password(username, password):
    admin_username = environ.get('ADMIN_USERNAME', 'admin')
    admin_password = environ.get('ADMIN_USERNAME', 'secret')
    return username is admin_username and password is admin_password


@app.route('/')
def home():
    return render_template('layout.html', form=SearchForm())


@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('home'))

    results = [
        Nyaa(query).run(),
        Pantsu(query).run(),
        YggTorrent(query).run(),
        YggAnimation(query).run(),
        AnimeUltime(query).run(),
    ]
    return render_template('search.html', form=SearchForm(), connectors=results)


@app.route('/latest')
def latest():
    torrents = [
        Nyaa('', return_type=ConnectorReturn.HISTORY, page=request.args.get('page', 1)).run(),
        Pantsu('', return_type=ConnectorReturn.HISTORY, page=request.args.get('page', 1)).run(),
        YggTorrent('', return_type=ConnectorReturn.HISTORY, page=request.args.get('page', 1)).run(),
        YggAnimation('', return_type=ConnectorReturn.HISTORY, page=request.args.get('page', 1)).run(),
        AnimeUltime('', return_type=ConnectorReturn.HISTORY, page=request.args.get('page', 1)).run(),
    ]

    results = []
    for torrent in torrents:
        results = results + torrent.data
    results.sort(key=itemgetter('date'))

    for keyword in AnimeTitle.query.all():
        for result in results:
            result['name'] = Connector.boldify(result['name'], keyword)

    return render_template('latest.html', form=SearchForm(), torrents=results)


@app.route('/list')
def list_animes():
    return 'Hello!'


@app.route('/admin')
@auth.login_required
def admin():
    return 'Hello!'


if __name__ == '__main__':
    app_debug = environ.get('FLASK_ENV', 'production') == 'development'
    app_port = environ.get('FLASK_PORT', 5000)
    app.run('0.0.0.0', app_port, app_debug)
