#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 24/2022 - Inital setup, group parsing functions and file searching SQL
#                   Feb 26/2022 - Adding input validation functions, not implementing WTForms
#                   
#
# Notes: There are a number of data handling steps that are repeated withnig multiple parts of the application.
# Migrating these functions to one or more modules allows reuse and simplifies the code needed in the the views 
# main.py and auth.py.
# 
# Currently this is a utility collection, group similar functions into commented sections to enable refactoring if
# the collection becomes too large.
 
#######################################################################################################################

import time, datetime, sys, os, mysql.connector, uuid, string
from mysql.connector import errorcode

from . import db, dbconnectalt
from . models import DataUser, User, DataGroup

########################################## User and Datauser Object parsing ###########################################
# 
# 
# This function parses the grouplist string stored for each datauser and converts the CSV string into a list opbject  
def getauthzfg(glstr):
    # remove any whitespaces in digit lists
    azlist=[x.strip(' ') for x in glstr.split(',')]
    return azlist






########################################## SQL statement creation ######################################################
# 
#
#  
# this function generates the SQL statement needed to retrieve a list of files that the user
# either owns or have been shared with a group the user is a member of, that also meets the 
# file search criteria. Although the function appears somewhat complex it forces the majority
# of the search effort back onto the database which is optimized for such things rather 
# than retrieving a larger record set and attempting to filter within the application.
#
# Function is simplified using optional arguments for search to create three different SQL statements
def getauthzfilesql(uid,authgroups,ftype,fname=None,fkeytag=None):
    # Define file meta-data to be selected from the database 
    sqlselect = "select uuid_hex,filename,keywords_tags,filetype,filecreate,filesize from storedfiles where" 
    # Generate the or conditions needed for the authgroup syntax in the where clause
    agsql="("
    grpcnt=len(authgroups) 
    for i in range(grpcnt):
        if i < (grpcnt -1):
            ag="authgroups={} or ".format(authgroups[i])
            agsql = agsql + ag
        else:
            ag="authgroups={}".format(authgroups[i])
            agsql = agsql + ag
    agsql = agsql + " ))"
    # Allow search filtering by filetype
    if ftype=="any":
        ftsql=" filetype is not null "
    else:
        ftsql=" filetype='{}' ".format(ftype)
    
    # start of SQL where clause
    sqlwhere=ftsql + "and (fileowner={} or ".format(uid)
    sqlwhere=sqlwhere + agsql
    
    # Adjust SQL where to include optional file name and/or keyword arguments
    #if (fname is None) and (fkeytag is None):
    #    sqlwhere = sqlwhere
    if (len(fname) > 0) and (len(fkeytag) == 0):
        sqlwhere=sqlwhere + " and (filename like '%{}%')".format(fname) 
    if (len(fname) == 0) and (len(fkeytag) > 0):
        sqlwhere=sqlwhere +  " and (keywords_tags like '%{}%')".format(fkeytag)
    # Future feature, search could include boolean logic between Keywords and file names
    # EG filename includes "sunspots" and keywords must contain "January" or not contain "Summer"
    if (len(fname) > 0) and (len(fkeytag) > 0):
        sqlwhere=sqlwhere + " and (filename like '%{}%' or keywords_tags like '%{}%')".format(fname,fkeytag)
    
    # Combine the parts to create the 
    fullsql=sqlselect + sqlwhere
    return fullsql

# This function generates the SQL needed to retrieve the binary large object data and set the mime type
# It also creates multiple where clause conditions to confirm the authenticated user is authorized to access
# this specific file. This prevents indirect object reference brute force attacks.
def getfiledatasql(uid,authgroups,fileuuid):
    sqlselect = "select filetype,filename,filedata from storedfiles "
    sqlwhere = "where uuid_hex='{}' and ( fileowner={} or ".format(fileuuid,uid)
    # convert string value into a list
    authgroups=getauthzfg(authgroups)
    # Generate the or conditions needed for the authgroup syntax in the where clause
    agsql="("
    grpcnt=len(authgroups) 
    for i in range(grpcnt):
        if i < (grpcnt -1):
            ag="authgroups={} or ".format(authgroups[i])
            agsql = agsql + ag
        else:
            ag="authgroups={}".format(authgroups[i])
            agsql = agsql + ag
    agsql = agsql + " ))"
    sqlwhere = sqlwhere + agsql
    # Combine the parts to create the 
    fullsql=sqlselect + sqlwhere
    return fullsql


def testfileownersql(fileuuid):
    if not isinstance(fileuuid,str):
        return None
    if len(fileuuid) != 32:
        return None
    else:
        sqlselect = "select fileowner,filename from storedfiles where uuid_hex='{}'".format(fileuuid)
        return sqlselect


def updatesharedgroupssql(grouplist,fileuuid):
    print(type(grouplist))
    #azglist = ','.join([str[x] for x in grouplist])
    azglist='01,02,03'
    updgrpsql="update storedfiles set authgroups='{}' where uuid_hex='{}'".format(azglist,fileuuid)
    return updgrpsql


###################  SQL database connections & queries ####################################
# 
#  Alternative connection to SQLAlchemy needed for file queries that reqquire customized 
#  SQL or only portions of the record row retrieved.  Eg, do not move all possible files 
#  into an object since that will exceed memory limits
#

#  These functions utilizes a database credential method for connection functions created in init.py
def getauthzfiles(dbconlist,appsql):
    try:
        dbhandle=dbconnectalt(dbconlist)
        thiscur=dbhandle.cursor()
        thiscur.execute(appsql)
        # get first 15 records
        tuplelist = thiscur.fetchmany(size=15)
        print(tuplelist)
        dbhandle.close()
    except Exception as err:
        print(err)
        return None
    # Presuming database query is successful
    if isinstance(tuplelist,list):
        print("process list")
        return tuplelist
    else:
        return None

def getfiledata(dbconlist,filesql):
    try:
        dbhandle=dbconnectalt(dbconlist)
        thiscur=dbhandle.cursor()
        thiscur.execute(filesql)
        # get filetype and blob
        resulttuple = thiscur.fetchone()
        #print(type(resulttuple))
        dbhandle.close()
    except Exception as err:
        print(err)
        return None
    if isinstance(resulttuple,tuple):
        # test if empty
        print("filetype: {}".format(resulttuple[0]))
        print(len(resulttuple[1]))
        return resulttuple
    else:
        return None

def testfileownership(dbconlist,ownersql):
    try:
        dbhandle=dbconnectalt(dbconlist)
        thiscur=dbhandle.cursor()
        thiscur.execute(ownersql)
        # get filetype and blob
        resulttuple = thiscur.fetchone()
        print(resulttuple)
        dbhandle.close()
    except Exception as err:
        print(err)
        return None
    return resulttuple

# This function retrieves the record set for each group the user is a member off
# The records are put into a dictionary so they can be used to advise the user about 
# which groups they may want to grant access to a file they own.
def getgroupdetails(azglist):
    azgroupdetails=dict()
    for azg in azglist:
        print(azg)
        tmplist=[]
        grouprecord=DataGroup.query.filter_by(groupid=azg).first()
        if grouprecord is not None:
            tmplist.append(grouprecord.groupname)
            tmplist.append(grouprecord.groupdesc)
            tmplist.append(grouprecord.grouptype)
            azgroupdetails[azg]=tmplist
    # creates a dictionary with a list for key data
    return azgroupdetails



############################  Database output processing ##################
#
def newresultsdict(resultlist):
    filemetadict = dict()
    if len(resultlist) > 0:
        for result in resultlist:
            filedate=result[4].strftime("%Y-%m-%d %H:%M:%S")
            if len(result[2]) > 15:
                keytagdisplay = result[2][:12] + " ..."
            else:
                keytagdisplay = result[2]
            # Convert integer to human friendly file size
            if result[5] > 1000000:
                fsize = "{} megabytes".format(str(round(float(result[5]/999999.9),2)))                
            elif result[5] > 1000 and result[5] < 1000000:
                fsize = "{} kilobytes".format(str(round(float(result[5]/999.9),2)))
            else:
                fsize = "{} bytes".format(str(result[5]))
            # converted data placed into a single string for dictionary
            keydata="{} {} {} {} {}".format(result[1].strip(),keytagdisplay,filedate,result[3],fsize)
            print("key: {}, Value: keydata ".format(result[0]))
            filemetadict[result[0]]=keydata
    else:
        print("<empty> HTML stuff")        

    return filemetadict

# This function creates a sepcific mime type based on the file extension passed to the function.
# The remaining response string can then be created to simiplify the response code on download.
# presumes the preceeding database responses for the binary byte stream and the file name are 
# refered to as fileblob and filename
def getmimetype(filetype):
    if filetype.lower()=="tar":
        truemime='application/xtar'
    elif filetype.lower()=="zip":
        truemime='application/zip'
    elif filetype.lower()=="pdf":
        truemime='application/pdf'
    elif filetype.lower()=="docx":
        truemime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif filetype.lower()=="jpg":
        truemime='image/jpeg'    
    elif filetype.lower()=="jpeg":
        truemime='image/jpeg'
    elif filetype.lower()=="png":
        truemime='image/png'
    elif filetype.lower()=="svg":
        truemime='image/svg+xml'
    elif filetype.lower()=="xls":
        truemime='application/vnd.ms-excel'
    elif filetype.lower()=="xlsx":
        truemime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif filetype.lower()=="csv":
        truemime='text/csv'
    else:
        truemime='text/plain'
    # once the mime type has been established return string
    return truemime


# This function converts the dictionary into a list of tuples for presentation
def newsharedgroups(shrgrpdict):
    presgrouplist=[]
    shrgrpitems=shrgrpdict.items()
    for item in shrgrpitems:
        gid=item[0]
        gname=item[1][0]
        if len(item[1][1]) > 30:
            gdesc=item[1][1][:27] + "..."
        else:
            gdesc=item[1][1]
        gdetails="{}: {}".format(gname,gdesc)
        presgrouplist.append((gid,gdetails))
    print(presgrouplist)
    return presgrouplist





#################################################  Input field validation ######################################

# This input check removes leading and trailing whitespace which could be benign
# If characters outside allowed list are found, the function replaces the string with "invalid_input", 
# function returns a list [bool,str]
def testuserstrps(ustr):
    strpustr=ustr.strip()
    # allow alphanumeric mixed case only
    allowlist=string.ascii_letters + string.digits
    for char in strpustr:
        if char not in allowlist:
            # exit immediately, return input for security monitoring but nullify the content
            defang="- - " + ustr + "- - "
            return [False,"invalid_input",defang]
    # return true only if for loop test comes back negative
    return [True,strpustr]


    


