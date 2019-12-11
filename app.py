from operator import itemgetter

from flask import redirect, render_template, request, url_for

from config import app, auth, db, ADMIN_USERNAME, ADMIN_PASSWORD, APP_PORT, IS_DEBUG
from connectors import *
from models import AnimeFolder, DeleteForm, SearchForm, EditForm


@auth.verify_password
def verify_password(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


@app.template_filter('boldify')
def boldify(name):
    query = request.args.get('q')
    name = Connector.boldify(name, query)
    for title in ConnectorCache.get_keywords():
        if title.keyword is not query:
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
    return render_template('layout.html', search_form=SearchForm())


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


@app.route('/admin')
@auth.login_required
def admin():
    folders = AnimeFolder.query.all()

    return render_template('admin/list.html', search_form=SearchForm(), folders=folders, delete_form=DeleteForm())


@app.route('/admin/delete', methods=['POST'])
@auth.login_required
def admin_delete():
    form = DeleteForm(request.form)
    if form.validate_on_submit():
        link = AnimeLink.query.filter_by(id=form.id.data).first()
        title = link.title
        db.session.delete(link)
        if not len(title.links):
            db.session.delete(title)
        db.session.commit()
    else:
        print(form.errors)
    return redirect(url_for('admin'))


@app.route('/admin/edit/<link_id>')
@auth.login_required
def admin_edit(link_id):
    link = AnimeLink.query.filter_by(id=link_id).first()
    edit_form = EditForm()
    edit_form.folder.choices = [(query.id, query.name) for query in AnimeFolder.query.all()]
    titles = AnimeTitle.query.all()

    return render_template('admin/edit.html', search_form=SearchForm(), link=link, titles=titles, edit_form=edit_form)


@app.route('/admin/add')
@auth.login_required
def admin_add():
    add_form = EditForm()
    add_form.folder.choices = [('', '')] + [(query.id, query.name) for query in AnimeFolder.query.all()]
    titles = AnimeTitle.query.all()

    return render_template('admin/add.html', search_form=SearchForm(), titles=titles, add_form=add_form)


@app.route('/admin/save', methods=['POST'])
@auth.login_required
def admin_save():
    form = EditForm(request.form)
    if form.validate_on_submit():
        folder = AnimeFolder.query.filter_by(id=form.folder)
        title = AnimeTitle.query.filter_by(name=form.name).first()
        title.folder = folder
        title.name = form.name
        title.keyword = form.keyword.lower() if form.keyword else title.keyword
        db.session.add(title)
        link = AnimeLink.query.filter_by(id=form.id)
        link.title = title
        link.link = form.link
        link.season = form.season
        link.comment = form.comment
        link.vf = form.is_vf
        db.session.add(link)
        db.session.commit()
    else:
        print(form.errors)
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run('0.0.0.0', APP_PORT, IS_DEBUG)
