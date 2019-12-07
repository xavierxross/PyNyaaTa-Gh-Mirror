from operator import itemgetter

from flask import redirect, render_template, url_for, request

from config import app, auth, ADMIN_USERNAME, ADMIN_PASSWORD, IS_DEBUG, APP_PORT, db
from connectors import *
from models import SearchForm, AnimeTitle


@auth.verify_password
def verify_password(username, password):
    return username is ADMIN_USERNAME and password is ADMIN_PASSWORD


@app.template_filter('boldify')
def boldify(name):
    query = request.args.get('q')
    name = Connector.boldify(name, query)
    for title in ConnectorCache.get_keywords():
        if title.keyword is not query:
            name = Connector.boldify(name, title.keyword)
    return name


@app.template_filter('shorten')
def shorten(str_to_replace):
    return str_to_replace[:30] + '...' if len(str_to_replace) > 30 else str_to_replace


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
    for result in results:
        result['self'] = Connector.get_instance(result['href'], '')
    results.sort(key=itemgetter('date'), reverse=True)

    return render_template('latest.html', form=SearchForm(), torrents=results, page=page)


@app.route('/list')
def list_animes():
    filters = None
    for i, to_filter in enumerate(request.args.get('s', 'nyaa,yggtorrent').split(',')):
        if not i:
            filters = AnimeLink.link.contains(to_filter)
        else:
            filters = filters | AnimeLink.link.contains(to_filter)

    titles = db.session.query(AnimeTitle, AnimeLink).join(AnimeLink).filter(filters).order_by(AnimeTitle.name).all()

    results = {}
    for title, link in titles:
        if title.id not in results:
            results[title.id] = [link]
        else:
            results[title.id].append(link)

    return render_template('list.html', form=SearchForm(), titles=results, connector=Connector, flags=ConnectorLang)


@app.route('/admin')
@auth.login_required
def admin():
    return 'Hello!'


if __name__ == '__main__':
    app.run('0.0.0.0', APP_PORT, IS_DEBUG)
