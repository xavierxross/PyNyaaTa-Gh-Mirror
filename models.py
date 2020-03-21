from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField
from wtforms.fields.html5 import SearchField, URLField
from wtforms.validators import DataRequired

from config import db


class AnimeFolder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=100, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    titles = db.relationship("AnimeTitle", backref="folder")


class AnimeTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=100, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    keyword = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('anime_folder.id'))
    links = db.relationship('AnimeLink', backref="title")


class AnimeLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    season = db.Column(db.Text(collation='utf8mb4_general_ci'), nullable=False)
    comment = db.Column(db.Text(collation='utf8mb4_general_ci'))
    vf = db.Column(db.Boolean, nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('anime_title.id'))


class SearchForm(FlaskForm):
    q = SearchField('search', validators=[DataRequired()])


class DeleteForm(FlaskForm):
    class Meta:
        csrf = False

    id = HiddenField('id', validators=[DataRequired()])


class EditForm(FlaskForm):
    id = HiddenField('id')
    folder = StringField('folder', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])
    link = URLField('link', validators=[DataRequired()])
    season = StringField('season', validators=[DataRequired()])
    comment = StringField('comment')
    keyword = StringField('keyword')
    is_vf = BooleanField('is_vf')


db.create_all()
