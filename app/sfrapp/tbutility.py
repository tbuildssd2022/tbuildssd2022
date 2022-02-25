#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 24/2022 - Inital setup, group parsing functions and file searching SQL
#                   
#
# Notes: There are a number of data handling steps that are repeated withnig multiple parts of the application.
# Migrating these functions to one or more modules allows reuse and simplifies the code needed in the the views 
# main.py and auth.py.
# 
# Currently this is a utility collection, group similar functions into commented sections to enable refactoring if
# the collection becomes too large.
 
#######################################################################################################################

import time, datetime, sys, os, mysql.connector, uuid
from mysql.connector import errorcode
from . import db, dbconnectalt
from . models import DataUser, User

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
    if (fname is not None) and (fkeytag is None):
        sqlwhere= "and (filename like '%{}%'}".format(fname) 
    if (fname is None) and (fkeytag is not None):
        sqlwhere= "and (keywords_tags like '%{}%'}".format(fkeytag)
    # Future feature, search could include boolean logic between Keywords and file names
    # EG filename includes "sunspots" and keywords must contain "January" or not contain "Summer"
    if (fname is not None) and (fkeytag is not None):
        sqlwhere= "and (filename like '%{}%' or keywords_tags like '%{}%'}".format(fname,fkeytag)
    
    # Combine the parts to create the 
    fullsql=sqlselect + sqlwhere
    return fullsql



###################  SQL database connections & queries ####################################
# 
#  Alternative connection to SQLAlchemy needed for file queries that reqquire customized 
#  SQL or only portions of the record row retrieved.  Eg, do not move all possible files 
#  into an object since that will exceed memory limits
#
#  This function utilizes a database credential method for connection functions created in init.py
#def dbconnectalt(dbhost,dbuser,dbcred,dbname):
#    try:
#        dbh = mysql.connector.connect(
#            host = dbhost,
#            user = dbuser,
#            password = dbcred,
#            database = dbname
#        )
#        return dbh
#    except Exception as err:
#        print(err)


def getauthzfiles(dbconlist,appsql):
    dbhandle=dbconnectalt(dbconlist)
    thiscur=dbhandle.cursor()
    result=thiscur.execute(appsql)
    # get first 15 records
    recordstuple = thiscur.fetchmany(size=15)
    print(type(result))
    print(recordstuple)
    dbhandle.close()
    return


    return
