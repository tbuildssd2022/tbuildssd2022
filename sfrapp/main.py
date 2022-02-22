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
from crypt import methods
from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup
from flask_login import  login_required, current_user
from werkzeug.security import generate_password_hash
from . import db
from . models import User
import os

main = Blueprint('main', __name__)

####################################  user authn ################################################################

# Inital page for unathenticated users, presents login section and message updates about the operating environment
@main.route('/')
def index():
    print("inside index function")
    #print(current_user.is_authenticated)
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


# If no valid session and access ID then redirect to login page.  Use
# Flask-login get_id method instead of writing something new. 
@main.route('/home')
#@login_required
def presenthome():
    print("inside present home")
    #print(current_user.is_authenticated)
    #if current_user.is_authenticated:
    #sessioncid=current_user.get_id()
    #account=User.query.filter_by(id=sessioncid).first()
    return render_template('home.html')


 #################################### File Transfers ##################################################   

# File search and download, 
# Place holder page for now, just validate for login
# This will be the main page for interacting with files the user has access to
# Format will be a list of up to 6 files, radio button selection and three buttons
# They can select a file for download, (one at a time)
# They can select a file to be shared with others (one at a time, also used to remove sharing if user is owner)
# They can select a file to be deleted (one at a time, they must be owner)
@main.route('/fsd1')
#@login_required
def presentfileview():
    print("inside present fileview")
    return render_template('fileview.html')
    

# File upload 
# Place holder page for now, just validate for login
# Possible IDS monitoring option, insider threat exploring the app once authenticated.
# Queries for active pages that don't end with a known valid number would generate 404 events
# Attacker would have no idea which ones were valid and we could also create a honeypot page
# that can only be accessed via indirect reference.
# replies with a 200, captures attacker data and triggers an alert, while presenting an old help page
# 
@main.route('/flup7')
#@login_required
def presentupload():
    print("inside present upload")
    return render_template('fileup.html')

# Response page 
@main.route('/flup2')
#@login_required
def proccessupload():
    # Runs file validator module 
    # (Haroun notes)
    # Convert file to blob,  ( V0 drop on /tmp to allow validator to work)
    # 
    return render_template('fileupresp.html')



########################################  Updates #########################################################

# File Share
@main.route('/fshr1', methods=['GET'])
#@login_required
def presentfileshare():
    print("inside present fileshare")
    return render_template('fileshare.html')


@main.route('/fshr4', methods=['POST'])
#@login_required
def processfileshare():
    return render_template('fileshareresp.html')




# These routes enable users to see what personally identifiable information about the authenticated user
# is included in the system, what groups they are currently a member of and presents a form to change their 
# password.  

@main.route('/ud2', methods=['GET'])
def showuser():
    print("inside show user")
    # get accessid from the session,
    # get uid for the user based on accessid ( need a common function, maybe hooked on all page loads?)
    # get groups list from datauser table, issue second query to groups table to get group details
    return render_template('userdetails.html')


@main.route('/ud4', methods=['POST'])
def updateuser():
    thisaccessid = request.form.get('aid')
    # confirm the user provided original password and accessid submitted matches aid in session 
    oldpassword = request.form.get('pwd')
    newpassword = request.form.get('pwd2')
    print(oldpassword)
    print(newpassword)
    # Temp placeholder before the database integration gets built out
    return render_template('userdetails.html')

