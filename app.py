from operator import itemgetter

from flask import redirect, render_template, request, url_for

from config import app, auth, db, ADMIN_USERNAME, ADMIN_PASSWORD, APP_PORT
from connectors import *
from models import AnimeFolder, AnimeTitle, DeleteForm, SearchForm, EditForm


@auth.verify_password
def verify_password(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


@app.template_filter('boldify')
def boldify(name):
    query = request.args.get('q')
    name = Connector.boldify(name, query)
    for title in AnimeTitle.query.all():
        if title.keyword != query:
            name = Connector.boldify(name, title.keyword)
    return name


@app.template_filter('flagify')
def flagify(is_vf):
    return ConnectorLang.FR.value if is_vf else ConnectorLang.JP.value


@app.template_filter('colorify')
def colorify(model):
    return Connector.get_instance(model.link, model.title.keyword).color


@app.route('/')
def home():
    return render_template('layout.html', search_form=SearchForm(), title='Animes torrents search engine')


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

    return render_template('search.html', search_form=SearchForm(), connectors=results)


@app.route('/latest')
@app.route('/latest/<int:page>')
def latest(page=1):
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

    return render_template('latest.html', search_form=SearchForm(), torrents=results, page=page)


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

    return render_template('list.html', search_form=SearchForm(), titles=results)


@app.route('/admin', methods=['GET', 'POST'])
@auth.login_required
def admin():
    folders = AnimeFolder.query.all()
    form = DeleteForm(request.form)

    if form.validate_on_submit():
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        if link:
            title = link.title
            db.session.delete(link)
            if not len(title.links):
                db.session.delete(title)
            db.session.commit()
            form.message = '%s (%s) has been successfully deleted' % (title.name, link.season)
        else:
            form._errors = {'id': ['Id %s was not found in the database' % form.id.data]}

    return render_template('admin/list.html', search_form=SearchForm(), folders=folders, action_form=form)


@app.route('/admin/edit', methods=['GET', 'POST'])
@app.route('/admin/edit/<int:link_id>', methods=['GET', 'POST'])
@auth.login_required
def admin_edit(link_id=None):
    titles = AnimeTitle.query.all()
    form = EditForm(request.form)
    form.folder.choices = [(query.id, query.name) for query in AnimeFolder.query.all()]

    if form.validate_on_submit():
        title = AnimeTitle.query.filter_by(name=form.name.data).first()
        title = title if title else AnimeTitle()
        title.folder_id = form.folder.data
        title.name = form.name.data
        title.keyword = form.keyword.data.lower() if form.keyword.data else title.keyword
        db.session.add(title)
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        link = link if link else AnimeLink()
        link.title_id = title.id
        link.link = form.link.data
        link.season = form.season.data
        link.comment = form.comment.data
        link.vf = form.is_vf.data
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('admin'))

    if link_id:
        link = AnimeLink.query.filter_by(id=link_id).first()
    else:
        link = AnimeLink()
        for attr in dir(link):
            if not attr.startswith('_') and getattr(link, attr) is None:
                try:
                    setattr(link, attr, '')
                except:
                    pass
        form.folder.choices = [(0, '')] + form.folder.choices

    return render_template('admin/edit.html', search_form=SearchForm(), link=link, titles=titles, action_form=form)


if __name__ == '__main__':
    app.run('0.0.0.0', APP_PORT, IS_DEBUG)
