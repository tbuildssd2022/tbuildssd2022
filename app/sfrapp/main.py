#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 18/2022 - Inital setup and variable cleanup
#                   Feb 21/2022 - Working through routing and HTML templates, working toward wireframes, 
#                               modified data model, built user admin tool etc.
#
# Notes: Main.py is the primary script used for routing the requests to the different URLs into the correct application
# log functions, (views?). Where possible, the presentation of the results and input forms will be done through HTML
# templates supported by cascading style sheets.
 
#######################################################################################################################
#from crypt import methods
from crypt import methods
from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup
from flask_login import  login_required, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import environ, path
from . import db, getconnectiondata,newdburi
from . models import DataUser, User
import os
# Import custom module classes and functions
from . tbutility import getauthzfg, getauthzfilesql, getauthzfiles



main = Blueprint('main', __name__)

####################################  user authn ################################################################

# Inital page for unathenticated users, presents login section and message updates about the operating environment
@main.route('/')
def index():
    print("inside index function")
    print(current_user.is_authenticated)
    return render_template('index.html')

# This is the home page for the data users 
# This should test for valid login and if so we should present a second
# version of the page that shows they are loggged in with an account
# and display the groups that user is a member of, as well as the current
# session ID. (use this for valdiating )
# Login button set to logout
#  ----- extended capabilities ----------
# Also looking at messages of the day.  
# Possibly a way to monitor for state changes, explore threading library
# and cleary identify all the risks of rolling your own threading based app
# instead of using well developed solutions like an MQTT callback.


# If no valid session and access ID then redirect to login page.
# Flask provides a method called login_required that protects access to
# any routes that include the @login_required decoration. This resolves 
# much of the OWASP broken authentication challenge through the use of a
# reliable framework instead of developing our own solution. 
# 
# Flask-login get_id method returns the authenticated user's numeric ID
# which can then be used to extract attributes from the Datauser class 
# such as group membership since this is an authorization requirement.

@main.route('/home')
@login_required
def presenthome():
    print("inside presenthome")
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        dname=thisdatauser.userdisplayname
        azglist=thisdatauser.authgroups
        # Debuging, comment out for production
        print(thisdatauser.userdisplayname)
        print(thisdatauser.useraccessid)
        print(thisdatauser.authgroups)
    # Use Jinja2 templates to prensent the authenticated user's personal data 
    # from server side database extraction, reducing user input injection points
    return render_template('home2.html', displayname=dname, grouplist=azglist )


 #################################### File Transfers ##################################################   

# File search and download, 
# Place holder page for now, just validate for login
# This will be the main page for interacting with files the user has access to
# Format will be a list of up to 6 files, radio button selection and three buttons
# They can select a file for download, (one at a time)
# They can select a file to be shared with others (one at a time, also used to remove sharing if user is owner)
# They can select a file to be deleted (one at a time, they must be owner)
@main.route('/fsd1', methods=['GET'])
@login_required
def presentfileview():
    print("inside present fileview")
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        azglist=thisdatauser.authgroups
        duaid=thisdatauser.useraccessid
        # To-Do  module function for retrieving group lists
    return render_template('filesearch.html',grouplist=azglist, aid=duaid )
    
@main.route('/fsd1', methods=['POST'])
@login_required
def presentfileview2():
    print("inside present fileview2 ")
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        azglist=thisdatauser.authgroups
        duserfilegroups=getauthzfg(azglist)
        #print(duserfilegroups)
        # Generate the SQL based on userid and group
        authzfilessql=getauthzfilesql(uid,duserfilegroups,"txt")
        #print(authzfiles)
        # Create database connection, then process SQL generated above
        dbcon = getconnectiondata()
        try:
            thisdbh = newdburi(dbcon)
            if thisdbh is not None:
                print("try the SQL")
                getauthzfiles(thisdbh,authzfilessql)
        except Exception as err:
            print(err)


    return render_template('fileview.html',filelist=authzfilessql)


# File upload 
# Place holder page for now, just validate for login
# Possible IDS monitoring option, insider threat exploring the app once authenticated.
# Queries for active pages that don't end with a known valid number would generate 404 events
# Attacker would have no idea which ones were valid and we could also create a honeypot page
# that can only be accessed via indirect reference.
# replies with a 200, captures attacker data and triggers an alert, while presenting an old help page
# 
@main.route('/flup7')
@login_required
def presentupload():
    print("inside present upload")
    return render_template('fileup.html')

# Response page 
@main.route('/flup2')
@login_required
def proccessupload():
    # Runs file validator module 
    # (Haroun notes)
    # Convert file to blob,  ( V0 drop on /tmp to allow validator to work)
    # 
    return render_template('fileupresp.html')



########################################  Updates #########################################################

# File Share
@main.route('/fshr1', methods=['GET'])
@login_required
def presentfileshare():
    print("inside present fileshare")
    return render_template('fileshare.html')


@main.route('/fshr4', methods=['POST'])
@login_required
def processfileshare():
    return render_template('fileshareresp.html')




# These routes enable users to see what personally identifiable information about the authenticated user
# is included in the system, what groups they are currently a member of and presents a form to change their 
# password.  

@main.route('/ud2', methods=['GET'])
@login_required
def showuser():
    print("inside show user")
    # get accessid from the session,
    # get uid for the user based on accessid ( need a common function, maybe hooked on all page loads?)
    # get groups list from datauser table, issue second query to groups table to get group details
    return render_template('userdetails.html')


@main.route('/ud4', methods=['POST'])
@login_required
def updateuser():
    thisaccessid = request.form.get('aid')
    # confirm the user provided original password and accessid submitted matches aid in session 
    oldpassword = request.form.get('pwd')
    newpassword = request.form.get('pwd2')
    print(oldpassword)
    print(newpassword)
    # Temp placeholder before the database integration gets built out
    return render_template('userdetails.html')




#############################################   testing ####################################
def getdatauser(aid):
    duserobj= DataUser.query.filter(DataUser.useraccessid==aid).first()
    return duserobj
    
def getauthnz(uidint):
    uauthznobj=User.query.filter(User.id==uidint).first()
    return uauthznobj

def verify_passwd(pwdhash,pwdstr):
    return check_password_hash(pwdhash,pwdstr)



@main.route('/login2', methods=['POST'] )
def login2():
    print("inside login 2")
    accessid = request.form.get('accessid')
    formpasswd = request.form.get('passwd')
    print(accessid)
    print(formpasswd)
    # Extract the UID from the datauser table for the accessid provided. 
    # password check is done against a second table  ( Move this to module)
    if accessid and formpasswd:
        # Move all this to a seperate module so we can valdiate all three things, pwdcheck should be last
        pwdchk=False # ensure authz check comes back true before proceeding
        thisduserobj=getdatauser(accessid)
        if isinstance(thisduserobj.userid,int):
            thisauthzobj=getauthnz(thisduserobj.userid)
        if thisauthzobj is not None:
            pwdchk=verify_passwd(thisauthzobj.userpasswd, formpasswd)
        if pwdchk:
            print("Setup login manager for this user")
            login_user(thisauthzobj)
        else:
            print("passwordcheck failed")
            

            #userauth=User.query.filter(User.userid==uid.userid).first()
            #if userauth is not None:
            #    print(userauth.userpasswd)
            #    print(userauth.activestatus)
            #    print(userauth.userlocked)

        
        #print(uid)
        #print(type(uid.userid))
        #print(uid.userid)
    #if current_user.is_authenticated:
    #   sessioncid=current_user.get_id()
    #    account=User.query.filter_by(id=sessioncid).first()
    #    msg='already authenticated as {}'.format(account.clientname)
    #    flash(msg)
    return render_template('home.html')
    #else:
    #    return render_template('index.html')