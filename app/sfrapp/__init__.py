#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 21/2022 - Updates to factory file 
#                   
#
# Notes: Initializes the flash application context
# https://hackersandslackers.com/flask-application-factory/
 
#######################################################################################################################
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv
from os import environ, path
from flask_login import LoginManager
from datetime import timedelta

# initialize the dabase object  so it is globally accessable
db = SQLAlchemy()

# Load the env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir,'.env'))

def getconnectiondata():
    condatalist=[]
    sfrdb=environ.get('dbinstance')
    username=environ.get('dbuser')
    cred=environ.get('dbcred')
    host=environ.get('dbhost')
    if not sfrdb:
        print("Missing database connection info: database instance name")
    else:
        condatalist.append(sfrdb)
    if not username:
        print("Missing database connection info: database user name")
    else:
        condatalist.append(username)
    if not cred:
        print("Missing database connection info: database credential")
    else:
        condatalist.append(cred)
    if not host:
        print("Missing database connection info: database host information")
    else:
        condatalist.append(host)
    if len(condatalist) !=4:
        print("missing database connection info, please correct")
        exit(1)
    else:
        return condatalist
    return False

def newdburi(connlist):
    # adjust based on order in list
    user=connlist[1]
    pwd=connlist[2]
    host=connlist[3]
    dbinst=connlist[0]
    #Create the database connection string while leaving the passwords external to the code.
    #dburi="mysql://{}:{}@{}:3306/{}".format(user,pwd,host,dbinst)
    # SQLAlchemy is requires the driver to be defined as well as the database type
    dburi="mysql+mysqlconnector://{}:{}@{}:3306/{}".format(user,pwd,host,dbinst)
    return dburi


def create_app():
    #Retrieves environment variables to make database connections,
    # avoids the need to store credentials in python scripts.
    connlist=getconnectiondata()
    dburi=newdburi(connlist)

    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_DATABASE_URI']=dburi
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=900)

    # Initialize SQLAlchemy plugin so is it globally accessable
    db.init_app(app)
    # Initialize Flask_login LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from .models import User
    from .models import DataUser
    @login_manager.user_loader
    def load_user(user_id):
        # client ID is the primary key of the user database
        return User.query.get(int(user_id))

    with app.app_context():
        ## auth components
        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint)

        # blueprint for non-auth views code
        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)


        # initialized app
        return app


