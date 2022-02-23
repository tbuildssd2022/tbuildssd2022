from crypt import methods
import flask
#import flask_login
from flask import Blueprint, render_template, redirect, url_for,flash, request
from flask_login import login_user,current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . models import User,DataUser
# Need this for the uncontrolled redirects ( unsupported but check it out)
from urllib.parse import urlparse, urljoin
#def is_safe_url(target):
#    ref_url = urlparse(request.host_url)
#    test_url = urlparse(urljoin(request.host_url, target))
#    return test_url.scheme in ('http', 'https') and \
#           ref_url.netloc == test_url.netloc


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


@auth.route('/login', methods=['POST'])
def login_post():
    accessid = request.form.get('accessid')
    formpasswd = request.form.get('passwd')
    print(accessid)
    print(formpasswd)
    # Need form validation on the accessid field.
    if accessid and formpasswd:
        thisduserobj=getdatauser(accessid)
        # Catches invalid user
        if thisduserobj is None:
            return redirect(url_for('main.index'))
        # Check password
        pwdchk=False # ensure authz check comes back true before proceeding
        if isinstance(thisduserobj.userid,int):
            thisauthzobj=getauthnz(thisduserobj.userid)
        if thisauthzobj is not None:
            pwdchk=verify_passwd(thisauthzobj.userpasswd, formpasswd)
        else:
            return redirect(url_for('main.index'))
        if pwdchk:
            print("Setup login manager for this user")
            login_user(thisauthzobj)
            return redirect(url_for('main.presenthome'))        
        else:
            print("passwordcheck failed")
            return redirect(url_for('main.index'))

   

# This should be checking for authentication status and if not redirect to the main index page. 
# It should already be protected by login required decoration but this would catch forceful browseing
@auth.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        authnzid=current_user.get_id()
        duserobj=getdatauid(authnzid)
        print(authnzid)
        print(type(authnzid))
        #account=User.query.filter_by(id=sessioncid).first()
        msg='already authenticated {}'.format(duserobj.userdisplayname)
        flash(msg)
        return redirect(url_for('main.presenthome'))
    else:
        return redirect(url_for('main.index'))
        #return render_template('index.html')


# Utilize Flask builtin user management to allow authenticated users to properly close their sessions
# OWASP session management requirement to prevent possible session hijacking attempts
@auth.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        authnzid=current_user.get_id()
        duserobj=getdatauid(authnzid)
        msg='already authenticated {}'.format(duserobj.userdisplayname)
        flash(msg)
        print("logging out user")
        logout_user()
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))
    #return render_template('index.html')
    #return 'Logout'