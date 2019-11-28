from app import db


class AnimeFolder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    titles = db.relationship("AnimeTitle", back_populates="folder")


class AnimeTitle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    keyword = db.Column(db.Text, nullable=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))
    folder = db.relationship('AnimeFolder', back_populates="titles")
    links = db.relationship('AnimeLink', back_populates="title")


class AnimeLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.Text, nullable=False)
    season = db.Column(db.Text, nullable=False)
    comment = db.Column(db.Text)
    vf = db.Column(db.Boolean, nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey('title.id'))
    title = db.relationship('AnimeTitle', back_populates="links")
