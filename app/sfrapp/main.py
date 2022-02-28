#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 18/2022 - Inital setup and variable cleanup
#                   Feb 21/2022 - Working through routing and HTML templates, working toward wireframes, 
#                               modified data model, built user admin tool etc.
#                   Feb 25/2022 - File search, file sharing, data model adjustments
#                   Feb 27/2022 - File upload and user details
#
# Notes: Main.py is the primary script used for routing the requests to the different URLs into the correct application
# log functions, (views?). Where possible, the presentation of the results and input forms will be done through HTML
# templates supported by cascading style sheets.
 
#######################################################################################################################
#from crypt import methods
from crypt import methods
import re
from flask import Blueprint,render_template, redirect,url_for, request, flash, Markup, send_file
from markupsafe import escape
from flask_login import  login_required, current_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from os import environ, path
from . import db, getconnectiondata,newdburi
from . models import DataUser, User, DataGroup
import io
# Import custom module classes and functions
from . tbutility import getauthzfg, getauthzfilesql, getauthzfiles,newresultsdict, getfiledatasql, getfiledata, getmimetype, testfileownersql,testfileownership,getgroupdetails, newsharedgroups,updatesharedgroupssql,updatesharedgrp,testfsradio,getfileextension,testfileextension,getcurdate,getnewuuid,newfileupload,getfiledeletesql



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
        if len(sfname) == 0:
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


# This route presents the HTML forms for the file upload feature.
# To ensure non-repudition, both the authenticated user's unique ID and the current time will be 
# included in the metadata of the uploaded file. To avoid tampering, this data will be collected
# serverside when the file content form is posted. 
#
# The unexpected routing URLS, flup7 posting to flup2 creates a possible IDS monitoring option,
# I.E., an insider threat exploring the app once authenticated with typically query for numerous
# URLs that follow naming conventions. 
# - Queries for active pages that don't end with a known valid number would generate 404 events and would
#   be more easily detectable through logparsing that relies on regular expressions.
# - Defining the specifc HTTP methods ensures "invalid method" errors can be highlighted since normal use
#   of the application should not generate such events.
# - Finally, an internal attacker may identify the numeric numeric convention and may periodically attempt
#   a few pages to avoid triggering detection. An unlinked page can be included in the application that appers
#   to be an older, forgotten portion of the application but in reality it captures the users's account information
#   and writes the data to the security log. This is commonly called a honey token or honey pot approach, and is one 
#   option for identifiying a sophisticated internal threat actor.
# 
@main.route('/flup7', methods=['GET'])
@login_required
def presentupload():
    print("inside presentupload /flup7")
    return render_template('fileup2.html')

# This route collects the file upload inputs, sanitizes those inputs, rejects suspicious content and identifies the authenticated user's id
# so file ownership can be established. 
@main.route('/flup2', methods=['POST'])
@login_required
def proccessupload():
    if current_user.is_authenticated:
        uid=current_user.get_id()
        # Collect this info for logging 
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        thisaid=thisdatauser.useraccessid
    #
    newfile = request.files['fileup']
    if newfile.filename == '':
        errmsg="No file was selected for uploading"
        flash(errmsg)
        return redirect(url_for('main.presentupload'))
    # Use werkzeug utility method for removing leading file paths occasionally used in application attacks
    newfilesecname=secure_filename(newfile.filename)
    flupkeytag=request.form.get('fileup-keyword-tag')
    # Use server side validation to prevent input errors when including keywords in the file storage action
    # Truncate the data rather than warning the user, 254 characters is more than adequate for reasonable needs
    # excessive uploads seems malicious ( tested with 3k of text, truncates as expected)
    if len(flupkeytag) > 254:
        flupkeytag = flupkeytag[:254]
    # Remove any potentially malicious HTML tags in this open user input field
    flupkeytag=escape(flupkeytag)
    # This is now set to selected by default so an unset value is a strong indicator of input tampering, as is invalid mime type
    fluptype=request.form.get('uploadedfiletype')
    if len(fluptype) == 0:
        errmsg="Please select the correct file type from the dropdown menu"
        flash(errmsg)
        return redirect(url_for('main.presentupload'))
    flupmimetest=getmimetype(fluptype)
    if flupmimetest=='invalid-mimetype':
        print("generate security event: Suspicious Mimetype attempted  {} ".format("- - "+flupmimetest+" - -"))
        errmsg="Please select the correct file type from the dropdown menu"
        flash(errmsg)
        return redirect(url_for('main.presentupload'))
    # Confirm valid extension
    flupext=getfileextension(newfilesecname)
    errmsg=testfileextension(flupext,fluptype)
    if errmsg is not None:
        flash(errmsg)
        return redirect(url_for('main.presentupload'))
    ###########################   End User input testing #########################################
    # Assuming no errors or suspicious activity with file upload input values begin processing the filedata itself.
    filedata = newfile.stream.read()  # assuming this is a byte stream
    filesize = len(filedata) # An array of bytes easily counted at insert,  useful meta data going forward
    if filesize > 64000000:
        errmsg="Maximum filesize has been exceeded"
        flash(errmsg)
        return redirect(url_for('main.presentupload'))
    # Build meta-data for file upload 
    filecreate = getcurdate()
    fileuuid = getnewuuid()
    #thisuploadsql=getfileuploadsql()
    uploadsql = ''' INSERT INTO storedfiles(uuid_hex,filename,filetype,filedata,fileowner,filecreate,filesize,keywords_tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) '''
    valuetuple = (fileuuid,newfilesecname,fluptype,filedata,uid,filecreate,filesize,flupkeytag)
    # Create database connection, then insert the complete file and meta-data 
    dbcondata = getconnectiondata()
    resultslist=newfileupload(dbcondata,uploadsql,valuetuple)
 
    return render_template('fileupresp.html',fname=newfilesecname,aid=thisaid)



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
                if selaction=="sharefile":
                    return redirect(url_for('main.presentfileshare',ukn=fileuuid))
                if selaction=="deletefile":
                    return redirect(url_for('main.delfile',ukn=fileuuid))
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

######################################### File Delete ########################################################
@main.route('/fdel2',methods=['GET'])
@login_required
def delfile():
    print("inside delete file method")
    # confirm the correct user is logged in
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
        thisaid=thisdatauser.useraccessid
    # get file information
    fileid=request.args.get('ukn')
    delsql=getfiledeletesql(uid,fileid)
    print(delsql)
    

    return render_template('filedelresp.html',aid=thisaid)



######################################### User Details ########################################################
# These routes enable users to see what personally identifiable information about the authenticated user
# is included in the system, what groups they are currently a member of and presents a form to change their 
# password.  

@main.route('/ud2', methods=['GET'])
@login_required
def showuser():
    print("inside show user")
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        userdisplay=dict()
        userdisplay['Account Access ID']=thisdatauser.useraccessid
        userdisplay['List of Authorized Groups']=thisdatauser.authgroups
        userdisplay['Space Agency Affiliation']=thisdatauser.useragency
        userdisplay['Forename']=thisdatauser.userforename
        userdisplay['Surname']=thisdatauser.usersurname
    print(userdisplay)

    # get accessid from the session,
    # get uid for the user based on accessid ( need a common function, maybe hooked on all page loads?)
    # get groups list from datauser table, issue second query to groups table to get group details
    return render_template('userdetails.html',udict=userdisplay)


@main.route('/ud4', methods=['POST'])
@login_required
def updateuser():
    if current_user.is_authenticated:
        uid=current_user.get_id()
        thisdatauser=DataUser.query.filter_by(userid=uid).first()
    if thisdatauser:
        userdisplay=dict()
        userdisplay['Account Access ID']=thisdatauser.useraccessid
        userdisplay['List of Authorized Groups']=thisdatauser.authgroups
        userdisplay['Space Agency Affiliation']=thisdatauser.useragency
        userdisplay['Forename']=thisdatauser.userforename
        userdisplay['Surname']=thisdatauser.usersurname
    # 
    thisaccessid = request.form.get('aid')
    # confirm the user provided original password and accessid submitted matches aid in session 
    oldpassword = request.form.get('pwd')
    newpassword = request.form.get('pwd2')
    print(oldpassword)
    print(newpassword)
    flash("Password change for account {}was successful".format(thisaccessid))
    # Temp placeholder before the database integration gets built out
    return render_template('userdetails.html',udict=userdisplay)