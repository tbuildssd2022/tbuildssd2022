from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'clients'
    userid = db.Column(db.Integer, primary_key=True)
    userforname = db.Column(db.String(45))
    usersurname = db.Column(db.String(45))
    userdisplayname = db.Column(db.String(90))
    useragency = db.Column(db.String(45))
    authgroups = db.Column(db.String(60))
    # Need to grab pwd from otehr table?  does this work?
    #pwd = db.Column(db.String(60))
    