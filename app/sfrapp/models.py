from flask_login import UserMixin
from . import db
from sqlalchemy.orm import deferred

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

class StoredFiles(db.Model):
    __tablename__ = 'storedfiles'
    uuid_hex = db.Column(db.String(32), primary_key=True)
    filename = db.Column(db.String(64))
    filetype = db.Column(db.String(8))
    filedata = deferred(db.Column(db.LargeBinary))
    fileowner = db.Column(db.Integer)
    authgroups = db.Column(db.String(60))
    filecreate = db.Column(db.Date)
    keywords_tags = db.Column(db.String(255))
    allowupdates = db.Column(db.Boolean)
    fileversion = db.Column(db.Integer())




    