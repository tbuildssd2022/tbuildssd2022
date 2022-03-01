#!/bin/env python3
#
# Build out some functions that we can import into various projects
# either within the code or from a python3 session
# EG.  
# >>>
# import tbsnippets
# >>> tbsnippets.file2mem(path-to-file)


# Define all libraries here

import time, datetime, sys, os, mysql.connector, uuid
from mysql.connector import errorcode




# File processing information.
# The app will need to read files from the upload and database retrieval into memory objects.
# This has time and memory consumption impacts as well as error handling requirements ( data type checking)

def file2memstats(filepath):
    start = time.time()
    # Get file on disk size and cap at 16 meg for now
    filesize = os.stat(filepath).st_size
    if (filesize > (32 * 1000 * 1024) ):
        print("file exceeded current limit\n")
        exit(1)
    # Read file into memory buffer as bytes rather than encoded string
    with open(filepath, 'rb') as fh:
        filecontent = fh.read()   # reads whole file
    stop = time.time()
    
    # output stats
    print("File size on disk is {} bytes\n".format(filesize))
    print("File loading time was {} seconds\n".format(stop - start))
    bytesused=sys.getsizeof(filecontent)
    print("File size in memory is {} bytes\n".format(bytesused))
    print("Memory object data type is: {}\n".format(type(filecontent)))
    
    # Clean up the object
    del filecontent



# Connect to the database 
# thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
# insert file metadata and bytes into a database
# SQL = ''' INSERT INTO blobsbx (filename,filebin) VALUES (%s,%s) ''' 
# get file metadata and bytes from the database for a specific file
#SQLGET = ''' SELECT filename,filebin from blobsbx WHERE id = '{0}' '''
# pass the id value as a formatted string
# cur.execute(SQLGET.format(str(2))) 
# Get a list of file names and IDs for any file with bytes
# SQLGETLIST = ''' SELECT id,filename from blobsbx WHERE filebin IS NOT NULL  '''

#  use host based restriction on SQL server as secondary control.  Must come from 10.100.200.0/24 only
# https://mysle.....

def sbxdbconnect(dbhost,dbuser,dbcred,dbname):
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



def file2mem(filepath):
    
    # Get file on disk size and cap at 32 meg for now, replace with filevalidator module
    filesize = os.stat(filepath).st_size
    if (filesize > (32 * 1000 * 1024) ):
        print("file exceeded current limit\n")
        exit(1)
    # Read file into memory buffer as bytes rather than encoded string
    with open(filepath, 'rb') as fh:
        filecontent = fh.read()   # reads whole file
    bytesused=sys.getsizeof(filecontent)
    print("File object in memory is {} bytes\n".format(bytesused))

    return filecontent


def mem2file(filepath,blob):
    try:
        with open(filepath,"wb") as wfh:
            wfh.write(blob)
            wfh.close()
    except Exception as err:
        print(err)
            # Clean up memory object too
    del blob
    return


# extract the current date and time, then format into MySQL datetime
# https://dev.mysql.com/doc/refman/8.0/en/datetime.html
def getcurdate():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Generate UUID on the MVC node, load into database as a hex value
# This is a consistent 16 byte value that can be converted back to a string for presenation.
# Stored as a string in mysql which could affect ordering in some scenarios
#  Using uuid4 to generate UUID that is system MAC agnostic https://docs.python.org/3/library/uuid.html
def getnewuuid():
    hexuuid = uuid.uuid4().hex
    return hexuuid

# Convert the hex number into a human readable string if needed for presentation
def getuuidstring(hexuuid):
    return str(uuid.UUID(hexuuid))

# this function takes some numeric arguments to manage the correct settings for the
# levels, types and categories. The numbers correspond to the location in the lists, making
# the logging protocol expandable and flexible should the need for different wording or 
# additional values be identified at some future time.

def newlogheader(ld,td,cd,uid=0):  # UID defaults to 0 and can be overridden    
    levelist=['debug','info','warning','error','critical']
    typelist=['ActivityTracking','EventOfInterest','AnomalousActivity','ApplicationError']
    categorylist=['URLAccess','AuthenticationSuccess','AuthenticationFailure','AuthorizationSuccess',
                    'AuthorizationFailure','AuthorizationChange','FileAccess','FileCreation',
                    'DatabaseException','ApplicationException']
    logmsgdict=dict()
    logmsgdict['eventlogtime']=datetime.datetime.now().isoformat(sep= ' ', timespec='milliseconds')
    logmsgdict['level']=levelist[ld]
    logmsgdict['type']=typelist[td]
    logmsgdict['category']=categorylist[cd]
    logmsgdict['userid']=uid

    return logmsgdict

# this function accepts a dictionary containing the log header values and a list of payload keys & values
def newlogmsg(lhd,lpl):
    # confirm there are an even number of keys & values
    if len(lpl)%2 !=0:
        payload=','.join(lpl)
        lpl=['InvalidPayload',payload]
    # Append the new keys and values to the dictionary
    for i in range(0,len(lpl),2):
        lhd[lpl[i]]=lpl[i+1]
    return lhd