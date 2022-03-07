#!/bin/env python3
# Author(s): Doug Leece
# Version history: Feb 21/2022 - Initial creation
#                   Mar 3/2022 - Adding function for default user group creation
# 
# Notes: A supporting module for the command line interfaces developed to support the creation, updating and deleting of datauser accounts
# Ensure this module file is saved to the same path as the mksfruser program.  
# 
#######################################################################################################################
# Define all module imports here

import datetime, mysql.connector
from werkzeug.security import generate_password_hash

# Connect to the database 
#  use host based restriction on SQL server as secondary control.  Must come from 10.100.200.0/24 only
#  https://dev.mysql.com/doc/mysql-secure-deployment-guide/5.7/en/secure-deployment-user-accounts.html

def devdbconnect(dbhost,dbuser,dbcred,dbname):
    try:
        dbh = mysql.connector.connect(
            host = dbhost,
            user = dbuser,
            password = dbcred,
            database = dbname
        )
        return dbh
    except mysql.connector.Error as err:
        print(err)
        return None


# extract the current date and time, then format into MySQL datetime
# https://dev.mysql.com/doc/refman/8.0/en/datetime.html
def getcurdate():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


#This function does a simple length check on the string provided for the password,
# string content is not validated as special characters are both encouraged and the
# string content itself is never stored in the database, only the hashed value of those bytes
# rendering any stored malicious content benign.
def checkgenpasswd(pwd):
    if len(pwd) < 10:
        print('password is too short, please re-enter')
        return None
    else:
        shpwd=generate_password_hash(pwd, method='pbkdf2:sha256',salt_length=16)
        return shpwd  

# This function check if the administrator has included a valid space agency name
#  if not, returns a specifc number to test for as an error condition,
#  if a valid agency, disregard the case and retrieve the group number through parsing a case statement
def checkuseragency(agency):
    agencylist=['canada','europe','japan','russia','usa']
    if agency.lower() not in agencylist:
        return int(99)
    if agency.lower()=="canada":
        return int(19)
    elif agency.lower()=="europe":
        return int(14)
    elif agency.lower()=="japan":
        return int(15)
    elif agency.lower()=="russia":
        return int(12)
    elif agency.lower()=="usa":
        return int(11)
    else:
        return(99)
