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
from . import db
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