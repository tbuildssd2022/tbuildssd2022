#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 22/2022 - Migrated login functions back into second view to seperate authentication from presentation
#                   and business logic
#                   Feb 23/2022 - Added logout function and Datauser object demonstration
#                   Feb 28/2022 - Created custom logging protocol for the application targeting sensitive areas of the
#                                   application that warrant more detailed logging than standard HTTP logging.  
#
# Notes: auth.py is the primary script used for user authentication. werkzeug built in functions are used for password
# validation, flask login method login_user is used to register each successfully authenticated user, allowing the seemless
# use of the login_required function on all protected pages to prevent unauthorized access. Two user objects are used,
# standard Flask User tracks authentication and account authorization elements for each user, Datauser tracks personal
# details like the user's name, space agency affiliation and file acccess group membership. This class could be easily
# extended in the future if more personalization is required without affecting authentication and account authorization.
#######################################################################################################################
#from crypt import methods  - test to see if this breaks
from ast import Str
from crypt import methods
import flask,logging
from flask import Blueprint, render_template, redirect, url_for,flash, request,current_app
from flask_login import login_user,current_user, logout_user, login_required
from werkzeug.security import check_password_hash
from . import db
from . models import User,DataUser
# Import custom module classes and functions
from . tbutility import testuserstrps,newlogheader,newlogmsg



auth = Blueprint('auth', __name__)


#############################################   Move to module ####################################
# Move all this to a seperate module so we can valdiate all three things, pwdcheck should be last
def getdatauser(aid):
    duserobj= DataUser.query.filter(DataUser.useraccessid==aid).first()
    return duserobj

def getdatauid(id):
    duserobj= DataUser.query.filter(DataUser.userid==id).first()
    return duserobj
    
def getauthnz(uidint):
    uauthznobj=User.query.filter(User.id==uidint).first()
    return uauthznobj

def verify_passwd(pwdhash,pwdstr):
    return check_password_hash(pwdhash,pwdstr)

#########################################################################################################

# This validates the access ID and password, failure redirects the user back to the main login page.
# The login is a two step process, access ID, which the user knows (& therefore could be compromised) is used
# to retrieve the user id, which is a numeric value the user doesn't ever know. This second user object is used
# to authenticate passwords but can also be used to lock the account and disable the account or force a password change.
# From a security monitoring perspective look for large numbers of HTTP 302 events from the same IP within a short time.
# This is indiciative of a credential stuffing, password spraying or brute force attacks. Since this is a post request the
# credentials used are not known so the three attacks are indistinguiable, hence the focus on rate and shared source.

@auth.route('/login', methods=['POST'])
def login_post():
    accessid = request.form.get('accessid')
    formpasswd = request.form.get('passwd')
    # Form validation on the accessid field for length.
    if isinstance(accessid,str) and len(accessid) > 0 and len(formpasswd) > 0:
        unametest=testuserstrps(accessid)
        if unametest[0]:
            thisduserobj=getdatauser(accessid)
            # Catches invalid user
            if thisduserobj is None:
                flash(" An access ID and password are required for authentication. Carefully retry your login, contact ISS ground station support if authentication issues persist.")
                # Result generated from unknown-invalid user input, high volumes of such events in a short time period 
                # are potentially a credential stuffing attack since the logon method does not faciliate enumeration
                payloadlist=['URL','/login','HTTPMethod',request.method,'FailureReason','UnknownUser','AccessID',accessid]
                logmsgdict = newlogheader(2,1,2)
                logmsg=newlogmsg(logmsgdict,payloadlist)
                print(logmsg)
                current_app.logger.warning(logmsg)
                return redirect(url_for('main.index'))
            # Check password
            pwdchk=False # ensure authz check comes back true before proceeding
            if isinstance(thisduserobj.userid,int):
                thisauthzobj=getauthnz(thisduserobj.userid)
            if thisauthzobj is not None:
                pwdchk=verify_passwd(thisauthzobj.userpasswd, formpasswd)
            else:
                print("Failed test 5, database corruption")
                flash(" An access ID and password are required for authentication. Carefully retry your login, contact ISS ground station support if authentication issues persist.")
                return redirect(url_for('main.index'))
            if pwdchk:
                #print("Setup login manager for this user")
                login_user(thisauthzobj)
                # Records the successful login event, capturing the accessID used, time stamp can be used to correlate 
                # source IP address with account, potentially useful if account compromise is suspected.
                payloadlist=['URL','/login','HTTPMethod',request.method,'SuccessReason','ValidCredentialUse','AccessID',accessid]
                logmsgdict = newlogheader(1,0,1)
                logmsg=newlogmsg(logmsgdict,payloadlist)
                print(logmsg)
                current_app.logger.info(logmsg)
                return redirect(url_for('main.presenthome'))        
            else:
                #print("Failed test 4, invalid password for valid user")
                flash(" An access ID and password are required for authentication. Carefully retry your login, contact ISS ground station support if authentication issues persist.")
                # Records the failed authentication attempt, capturing the accessID used, time stamp can be used to correlate 
                # source IP address with account used. High volumes of failed authencation and multiple usernames is indicative
                # of a password spraying attack. Knowing which account IDs are being attempted can provide insight into whether
                # internal data like a userlist is in the hands of the attacker - potential insider threat or indicator of previous 
                # data loss event that may not have been detected.
                payloadlist=['URL','/login','HTTPMethod',request.method,'FailureReason','InvalidPassword','AccessID',accessid]
                logmsgdict = newlogheader(2,1,2)
                logmsg=newlogmsg(logmsgdict,payloadlist)
                print(logmsg)
                current_app.logger.warning(logmsg)
                return redirect(url_for('main.index'))
        else:
            flash(" An access ID and password are required for authentication. Carefully retry your login, contact ISS ground station support if authentication issues persist.")
            #print("Failed test 2, Suspicious Username, write to IDS: {}".format(unametest[2]) )
            # Result generated from user input that does not confirm to known accessID format, highly unlikley to be an
            # honest user mistake, highly suspicious so it is being raised to a higher threshold 
            payloadlist=['URL','/login','HTTPMethod',request.method,'FailureReason','InvalidInputCharacters','AccessID',unametest[2]]
            logmsgdict = newlogheader(2,2,2)
            logmsg=newlogmsg(logmsgdict,payloadlist)
            print(logmsg)
            current_app.logger.warning(logmsg)
            return redirect(url_for('main.index'))
    else:
        #print("failed test 1, missing one of two required fields,")
        flash(" An access ID and password are required for authentication. Carefully retry your login, contact ISS ground station support if authentication issues persist.")
        return redirect(url_for('main.index'))

   
# This checks for authentication status and redirects the user to the app home page while presenting their display name.
# If not authenticated it redirects to the main index page which presents a login prompt. 

@auth.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        authnzid=current_user.get_id()
        duserobj=getdatauid(authnzid)
        #print(authnzid)
        #print(type(authnzid))
        msg='already authenticated as {}'.format(duserobj.userdisplayname)
        flash(msg)
        return redirect(url_for('main.presenthome'))
    else:
        return redirect(url_for('main.index'))



# Utilize Flask builtin user management to allow authenticated users to properly close their sessions
# OWASP session management requirement to prevent possible session hijacking attempts
# Using the login required decorator ensures the logout_user method will only be applied to 
# authenticated users. Modifying the message demonstrates the use of objects, this is a datauser object
# which is instantiated to track all personal information about the user, not the default flask user object
# which was extended to track advanced authentication and authorization measures.
@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    if current_user.is_authenticated:
        authnzid=current_user.get_id()
        duserobj=getdatauid(authnzid)
        msg='Logging out the following user access id: {} '.format(duserobj.useraccessid)
        flash(msg)
        logout_user() 
         # Records the time a user account logged out of the application, potentially important to an investigation if there is
         # dispute over user activity, time worked etc.
        payloadlist=['URL','/logout','HTTPMethod',request.method,'AccessID',duserobj.useraccessid]
        logmsgdict = newlogheader(1,0,1)
        logmsg=newlogmsg(logmsgdict,payloadlist)
        print(logmsg)
        current_app.logger.info(logmsg)
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))  