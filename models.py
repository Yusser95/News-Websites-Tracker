
from app import db


class Domain(db.Model):
    __tablename__ = 'domains'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100000), nullable=False)
    status = db.Column(db.String(100000), nullable=True)



class Keyword(db.Model):
    __tablename__ = 'keywords'

    id = db.Column(db.Integer, primary_key=True)
    en_word = db.Column(db.String(100000),  nullable=True)
    ch_word = db.Column(db.String(100000),  nullable=False) # unique=True





class Pargraph(db.Model):
    __tablename__ = 'pargraphs'

    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer ,  nullable=False)
    text = db.Column(db.String(100000),  nullable=False)
    html = db.Column(db.String(100000),  nullable=True)
    file_name = db.Column(db.String(100000),  nullable=True)



class Keyword_Pargraph(db.Model):
    __tablename__ = 'keywords_pargraphs'

    id = db.Column(db.Integer, primary_key=True)
    pargraph_id = db.Column(db.Integer,  nullable=False)
    keyword_id = db.Column(db.Integer,  nullable=False)


class Settings_Schedule(db.Model):
    __tablename__ = 'settings_schedule'

    id = db.Column(db.Integer, primary_key=True)
    activate = db.Column(db.String(100000),  nullable=True)
    days = db.Column(db.Integer,  nullable=True)



