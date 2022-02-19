#!/bin/env python3
#
# Build out some functions that we can import into various projects
# either within the code or from a python3 session
# EG.  
# >>>
# import tbsnippets

# Define all libraries here

import time, datetime, sys, os




# File processing information.
# The app will need to read files from the upload and database retrieval into memory objects.
# This has time and memory consumption impacts as well as error handling requirements ( data type checking)

def file2mem(filepath):
    start = datetime.time()
    # Get file on disk size and cap at 16 meg for now
    filesize = os.stat(filepath).st_size
    if (filesize > (16 * 1000 * 1024) ):
        print("file exceeded current limit\n")
        exit(1)
    # Read file into memory buffer
    with open(filepath, 'r') as fh:
        filecontent = fh.read()   # reads whole file
    stop = datetime.time()
    
    # output stats
    print("File size on disk is {} bytes\n".format(filesize))
    print("File loading time was {} microseconds\n".format(stop - start))
    bytesused=sys.getsizeof(filecontent)
    print("File size in memory is {} bytes\n".format(bytesused))
    print("Memory object is: {}\n".format(type(filecontent)))
    
    # Clean up the object
    del filecontent






