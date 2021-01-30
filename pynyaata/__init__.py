from asyncio import get_event_loop, set_event_loop, SelectorEventLoop
from functools import wraps
from operator import attrgetter, itemgetter

import requests
from flask import redirect, render_template, request, url_for, abort, json
from requests import RequestException

from . import utils
from .config import app, auth, logger, scheduler, ADMIN_USERNAME, ADMIN_PASSWORD, MYSQL_ENABLED, APP_PORT, IS_DEBUG, \
    CLOUDPROXY_ENDPOINT
from .connectors import get_instance, run_all
from .connectors.core import ConnectorLang, ConnectorReturn
from .forms import SearchForm, DeleteForm, EditForm

if MYSQL_ENABLED:
    from .config import db
    from .models import AnimeFolder, AnimeTitle, AnimeLink


def mysql_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not MYSQL_ENABLED:
            return abort(404)
        return f(*args, **kwargs)

    return decorated_function


@auth.verify_password
def verify_password(username, password):
    return username == ADMIN_USERNAME and ADMIN_PASSWORD == password


@app.template_filter('boldify')
def boldify(name):
    query = request.args.get('q', '')
    name = utils.boldify(name, query)
    if MYSQL_ENABLED:
        for keyword in db.session.query(AnimeTitle.keyword.distinct()).all():
            if keyword[0].lower() != query.lower():
                name = utils.boldify(name, keyword[0])
    return name


@app.template_filter('flagify')
def flagify(is_vf):
    return ConnectorLang.FR.value if is_vf else ConnectorLang.JP.value


@app.template_filter('colorify')
def colorify(model):
    return get_instance(model.link, model.title.keyword).color


@app.context_processor
def inject_user():
    return dict(mysql_disabled=not MYSQL_ENABLED)


@app.route('/')
def home():
    return render_template('layout.html', search_form=SearchForm(), title='Animes torrents search engine')


@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return redirect(url_for('home'))

    set_event_loop(SelectorEventLoop())
    return render_template('search.html', search_form=SearchForm(),
                           connectors=get_event_loop().run_until_complete(run_all(query)))


@app.route('/latest')
@app.route('/latest/<int:page>')
def latest(page=1):
    set_event_loop(SelectorEventLoop())
    torrents = get_event_loop().run_until_complete(run_all('', return_type=ConnectorReturn.HISTORY, page=page))

    results = []
    for torrent in torrents:
        results = results + torrent.data
    for result in results:
        result['self'] = get_instance(result['href'])
    results.sort(key=itemgetter('date'), reverse=True)

    return render_template('latest.html', search_form=SearchForm(), torrents=results, page=page)


@app.route('/list')
@app.route('/list/<url_filters>')
@mysql_required
def list_animes(url_filters='nyaa,yggtorrent'):
    filters = None
    for i, to_filter in enumerate(url_filters.split(',')):
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

    return render_template('list.html', search_form=SearchForm(), titles=results)


def remove_garbage(link):
    title = link.title
    if title and not len(title.links):
        db.session.delete(title)
        db.session.commit()


@app.route('/admin', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def admin():
    form = DeleteForm(request.form)

    if form.validate_on_submit():
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        if link:
            form.message = '%s (%s) has been successfully deleted' % (link.title.name, link.season)
            db.session.delete(link)
            db.session.commit()
            remove_garbage(link)
        else:
            form._errors = {'id': ['Id %s was not found in the database' % form.id.data]}

    folders = AnimeFolder.query.all()
    for folder in folders:
        for title in folder.titles:
            title.links.sort(key=attrgetter('season'))
        folder.titles.sort(key=attrgetter('name'))

    return render_template('admin/list.html', search_form=SearchForm(), folders=folders, action_form=form)


@app.route('/admin/edit', methods=['GET', 'POST'])
@app.route('/admin/edit/<int:link_id>', methods=['GET', 'POST'])
@mysql_required
@auth.login_required
def admin_edit(link_id=None):
    folders = AnimeFolder.query.all()
    form = EditForm(request.form)

    if form.validate_on_submit():
        # Instance for VF tag
        instance = get_instance(form.link.data)
        # Folder
        folder = AnimeFolder.query.filter_by(name=form.folder.data).first()
        folder = folder if folder else AnimeFolder()
        folder.name = form.folder.data
        db.session.add(folder)
        db.session.commit()
        # Title
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        link = link if link else AnimeLink()
        title = AnimeTitle.query.filter_by(id=link.title_id).first()
        title = title if title else AnimeTitle.query.filter_by(name=form.name.data).first()
        title = title if title else AnimeTitle()
        title.folder_id = folder.id
        title.name = form.name.data
        title.keyword = form.keyword.data.lower() if form.keyword.data else title.keyword
        db.session.add(title)
        db.session.commit()
        # Link
        link.title_id = title.id
        link.link = form.link.data
        link.season = form.season.data
        link.comment = form.comment.data
        link.vf = instance.is_vf(form.link.data)
        db.session.add(link)
        db.session.commit()
        remove_garbage(link)
        return redirect(url_for('admin'))

    if link_id:
        link = AnimeLink.query.filter_by(id=link_id).first()
        form.folder.data = link.title.folder.id
    else:
        link = utils.clean_model(AnimeLink())
        link.title = utils.clean_model(AnimeTitle())
        link.vf = False

    return render_template('admin/edit.html', search_form=SearchForm(), link=link, folders=folders, action_form=form)


@scheduler.task('interval', id='flaredestroyy', days=1)
def flaredestroyy():
    if CLOUDPROXY_ENDPOINT:
        try:
            json_session = requests.post(CLOUDPROXY_ENDPOINT, data=json.dumps({
                'cmd': 'sessions.list'
            }))
            response = json.loads(json_session.text)
            sessions = response['sessions']

            for session in sessions:
                requests.post(CLOUDPROXY_ENDPOINT, data=json.dumps({
                    'cmd': 'sessions.destroy',
                    'session': session
                }))
                logger.info('Destroyed %s' % session)
        except RequestException as e:
            logger.exception(e)


def run():
    app.config['SQLALCHEMY_ECHO'] = IS_DEBUG
    scheduler.start()
    flaredestroyy()
    app.run('0.0.0.0', APP_PORT, IS_DEBUG)
