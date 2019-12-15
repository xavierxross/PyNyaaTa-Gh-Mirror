from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField, StringField
from wtforms.fields.html5 import SearchField, URLField
from wtforms.validators import DataRequired

from config import db


class AnimeFolder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False, collation='utf8mb4_general_ci')
    titles = db.relationship("AnimeTitle", backref="folder")


class AnimeTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False, collation='utf8mb4_general_ci')
    keyword = db.Column(db.Text, nullable=False, collation='utf8mb4_general_ci')
    folder_id = db.Column(db.Integer, db.ForeignKey('anime_folder.id'))
    links = db.relationship('AnimeLink', backref="title")


class AnimeLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False, collation='utf8mb4_general_ci')
    season = db.Column(db.Text, nullable=False, collation='utf8mb4_general_ci')
    comment = db.Column(db.Text, collation='utf8mb4_general_ci')
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
    folder = SelectField('folder', validators=[DataRequired()], coerce=int)
    name = StringField('name', validators=[DataRequired()])
    link = URLField('link', validators=[DataRequired()])
    season = StringField('season', validators=[DataRequired()])
    comment = StringField('comment')
    keyword = StringField('keyword')
    is_vf = BooleanField('is_vf')


db.create_all()
