from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'userauthnz'
    id = db.Column(db.Integer, primary_key=True)
    userpasswd = db.Column(db.String(102))
    userlocked = db.Column(db.Integer)
    activestatus = db.Column(db.Integer)
    forcepwdchange = db.Column(db.Integer)
    #
class DataUser(UserMixin, db.Model):
    __tablename__ = 'datauser'
    userid = db.Column(db.Integer, primary_key=True)
    userforename = db.Column(db.String(45))
    usersurname = db.Column(db.String(45))
    userdisplayname = db.Column(db.String(90))
    useragency = db.Column(db.String(45))
    useraccessid = db.Column(db.String(12))
    authgroups = db.Column(db.String(60))
    #
   
    