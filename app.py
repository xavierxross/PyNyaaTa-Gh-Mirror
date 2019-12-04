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
    page = request.args.get('page', 1)

    torrents = [
        Nyaa('', return_type=ConnectorReturn.HISTORY, page=page).run(),
        Pantsu('', return_type=ConnectorReturn.HISTORY, page=page).run(),
        YggTorrent('', return_type=ConnectorReturn.HISTORY, page=page).run(),
        YggAnimation('', return_type=ConnectorReturn.HISTORY, page=page).run(),
        AnimeUltime('', return_type=ConnectorReturn.HISTORY, page=page).run(),
    ]

    results = []
    for torrent in torrents:
        results = results + torrent.data
    results.sort(key=itemgetter('date'), reverse=True)

    for keyword in AnimeTitle.query.all():
        for result in results:
            result['name'] = Connector.boldify(result['name'], keyword)

    for result in results:
        result['self'] = Connector.get_instance(result['href'], '')

    return render_template('latest.html', form=SearchForm(), torrents=results, page=page)


@app.route('/list')
def list_animes():
    results = []

    return render_template('list.html', form=SearchForm(), torrents=results)


@app.route('/admin')
@auth.login_required
def admin():
    return 'Hello!'


if __name__ == '__main__':
    app_debug = environ.get('FLASK_ENV', 'production') == 'development'
    app_port = environ.get('FLASK_PORT', 5000)
    app.run('0.0.0.0', app_port, app_debug)
