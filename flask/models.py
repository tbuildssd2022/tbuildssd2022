from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'usercredential'
    userid = db.Column(db.Integer, primary_key=True)
    userpasswd = db.Column(db.String(45))
    userlocked = db.Column(db.Integer)
    activestatus = db.Column(db.Integer)
    forcepwdchange = db.Column(db.Integer)
    #
    #userforname = db.Column(db.String(45))
    #usersurname = db.Column(db.String(45))
    #userdisplayname = db.Column(db.String(90))
    #useragency = db.Column(db.String(45))
    #authgroups = db.Column(db.String(60))
    #
    # Need to grab pwd from otehr table?  does this work?
    #pwd = db.Column(db.String(60))
    