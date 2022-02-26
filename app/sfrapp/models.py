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

# Not practical to use as an object class as there could be thousands of files
# Deferred may prevent blobs being loaded into memory on search but custom SQL
# allows additional checks and more intuitive selection criteria
# 
# class StoredFiles(db.Model):
#    __tablename__ = 'storedfiles'
#    uuid_hex = db.Column(db.String(32), primary_key=True)
#    filename = db.Column(db.String(64))
#    filetype = db.Column(db.String(8))
#    filedata = deferred(db.Column(db.LargeBinary))
#    fileowner = db.Column(db.Integer)
#    authgroups = db.Column(db.String(60))
#    filecreate = db.Column(db.Date)
#    filesize = db.Column(db.Integer)
#    keywords_tags = db.Column(db.String(255))
3    # Schema extension needed for file versioning or multi-user update options
#    #allowupdates = db.Column(db.Boolean)
#    #fileversion = db.Column(db.Integer())


class DataGroup(db.Model):
    __tablename__ = 'datagroups'
    groupid = db.Column(db.String(2), primary_key=True)
    groupname = db.Column(db.String(45))
    groupdesc = db.Column(db.String(90))
    grouptype = db.Column(db.Integer)




    