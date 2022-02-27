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
import re
from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup, send_file
from flask_login import  login_required, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import environ, path
from . import db, getconnectiondata,newdburi
from . models import DataUser, User, DataGroup
import io
# Import custom module classes and functions
from . tbutility import getauthzfg, getauthzfilesql, getauthzfiles,newresultsdict, getfiledatasql, getfiledata, getmimetype, testfileownersql,testfileownership,getgroupdetails, newsharedgroups,updatesharedgroupssql,updatesharedgrp,testfsradio



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
        thisaid=thisdatauser.useraccessid
        azglist=thisdatauser.authgroups
        duserfilegroups=getauthzfg(azglist)
        # Generate the SQL based on userid and group for authorization
        # function call modifies SQL based on search fields being populated
        sftype=request.form.get('selectedfiletype')
        sfname=request.form.get('filename')
        skeytag=request.form.get('keyword-tag')
        authzfilessql=getauthzfilesql(uid,duserfilegroups,sftype,sfname,skeytag)
        if len(sftype) == 0:
            sfname="any file name"
        if len(skeytag) == 0:
            skeytag="any keywords"
        # Create database connection, then process SQL generated above
        dbcondata = getconnectiondata()
        resultslist=getauthzfiles(dbcondata,authzfilessql) 
        if resultslist is not None and len(resultslist) > 0:
            # New function to turn the tuples into a dictionary
            authzdict=newresultsdict(resultslist)
        else:
            authzdict = dict()
            authzdict['00000000000000000000000000000000']="No available files were indentified for this search: {} ".format(sftype)
    return render_template('fileview2.html',azfiledict=authzdict,aid=thisaid,grouplist=azglist,searchfname=sfname,searchkeytag=skeytag,searchtype=sftype)


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
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        thisaid=thisdatauser.useraccessid
        azglist=thisdatauser.authgroups
        # Parse the string into two digit list values
        azglist=getauthzfg(azglist)
        usergroupdict=getgroupdetails(azglist)
        fileid=request.args.get('ukn')
        # confirm user belongs to at least one group
        if len(usergroupdict) > 0:
            thisprezgroups=newsharedgroups(usergroupdict)
            print(thisprezgroups)
    return render_template('fileshare.html',prezgroups=thisprezgroups,ukn=fileid)


@main.route('/fshr4', methods=['POST'])
@login_required
def processfileshare():
    if current_user.is_authenticated:
        uid=current_user.get_id()
    checkshared=request.form.getlist('sharedgroups')
    fileid=request.form.get('ukn2')
    
    updategrpsql=updatesharedgroupssql(checkshared,fileid,uid)
    # Create database connection, then process SQL generated above
    dbcondata = getconnectiondata()
    updatesharedgrp(dbcondata,updategrpsql)

    return render_template('fileshareresp.html')


######################################### File Download ########################################################
@main.route('/fsd5',methods=['POST'])
@login_required
def getdownload():
    # Error handling for unchecked radio buttons, since we are avoiding client side javascript
    # to avoid browser compatibility issues and client side attack surface
    print("inside fsd5")
    fileuuid=request.form.get('fileselection')
    selaction=request.form.get('actionrequest')
    # User input validation & anomalous detection measure
    errmsg=testfsradio(fileuuid,selaction)
    print(errmsg)
    if errmsg is not None:
        print(errmsg)
        flash(errmsg)
        return redirect(url_for('main.presentfileview'))
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
        azglist=thisdatauser.authgroups
        aid=thisdatauser.useraccessid
        # Determine the user's requested action and develop the correct query
        # The first requirement is to determine if the authenticated user is the 
        # current owner of the file requested, otherwise generate an error message
        if selaction=="sharefile" or selaction=="deletefile":
            tfosql=testfileownersql(fileuuid)
            dbcondata = getconnectiondata()
            tforesult=testfileownership(dbcondata,tfosql)
            if int(tforesult[0]) != int(uid):
                errmsg="Account {} is not currently the authorized owner of file {}".format(aid, tforesult[1])
                print(errmsg)
                flash(errmsg)
                #print("Account {} is not currently the authorized owner of file {}".format(aid, tforesult[1]))
                return redirect(request.referrer)
            else:
                return redirect(url_for('main.presentfileshare',ukn=fileuuid))
        else:
            # Download file is expected to be the most common action
            #Rerun Need a second check to confirm user ID is permitted to access this file
            #Prevents insecure direct object reference attempts by authenticated users
            print("Checking if UID {} , in these groups {}, can access this file {} ".format(uid,azglist,fileuuid))
            thissql=getfiledatasql(uid,azglist,fileuuid)
            # Assuming this comes back OK we need to now make the SQL to grab the file
            dbcondata = getconnectiondata()
            thisfilereq=getfiledata(dbcondata,thissql)
            #print(type(thisfilereq))
            if thisfilereq is None:
                return render_template('filedownloadfailure.html',tempprint=thissql)
            else:
                filetype=thisfilereq[0] 
                filename=thisfilereq[1]
                fileblob=io.BytesIO(thisfilereq[2])  # Convert the byte array into something send-file can read
                # The filetype is used to determine the correct mimetype for the http response 
                newmime=getmimetype(filetype)
                return send_file(fileblob, as_attachment=True, download_name=filename, mimetype=newmime)
    # Redirect unauthenticated users
    else:
        return render_template('index.html')

# This route should never be taken,  post in the only method expected. 
# Forceful browsing/scanning or insecure direct object reference attempts by unauthenticated users
@main.route('/fsd5',methods=['GET'])
def presentdlredirect():
    return render_template('index.html')


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