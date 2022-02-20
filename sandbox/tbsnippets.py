#!/bin/env python3
#
# Build out some functions that we can import into various projects
# either within the code or from a python3 session
# EG.  
# >>>
# import tbsnippets
# >>> tbsnippets.file2mem(path-to-file)


# Define all libraries here

import time, datetime, sys, os, mysql.connector
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