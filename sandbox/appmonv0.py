#!/bin/env python3
# Author(s): Doug Leece
# Version history: Mar 1/2022 - Initial creation
#
# Attempting to keep this native python instead of OS specific shelling out to tail -f
# Starting with this : https://medium.com/@aliasav/how-follow-a-file-in-python-tail-f-in-python-bca026a901cf
#
################################################################################################################
import time, os, datetime, re, json
from ast import literal_eval  # a safe way to convert the string to a dictionary

# This function receives security event logs of all severity and writes to a daily file.
def updatesecevt(evtline):
    # Create a new logfile daily
    dstamp=datetime.datetime.now().strftime("%Y%m%d")
    secevtlog="/var/tmp/secevt-{}.log".format(dstamp)
    # Remove the Python logging headers to expose the dictionary
    # string that can be turned into JSON
    relinesplit= re.search('^\w+:\w+:(.*)',evtline)
    if relinesplit is not None:
        loglinestr=relinesplit.group(1)
        loglinedict=literal_eval(loglinestr)
        with open(secevtlog, "a+") as secevtfh:
            json.dump(loglinedict, secevtfh)
            secevtfh.write("\n")
    return

def updatehttpevt(evtline):
    # Create a new logfile daily
    dstamp=datetime.datetime.now().strftime("%Y%m%d")
    httpevtlog="/var/tmp/httpevt-{}.log".format(dstamp)
    # Remove the Python logging headers to create NCSA format log
    relinesplit= re.search('^\w+:\w+:(.*)',evtline)
    if relinesplit is not None:
        ncsalogline=relinesplit.group(1)
        with open(httpevtlog, "a+") as httpevtfh:
            httpevtfh.write(ncsalogline + "\n" )
    return

# This function sorts the incoming log events into HTTP event and application event logs
# HTTP logs are high volume and do not contain the contextual information of the custom
# application logs. The logs are filtered into two different files to allow ingestion into 
# a centralized security monitoring solution.  
def filterline(thisline):
    
    # Using a case statement instead of regex for speed and reliable parsing
    if thisline.startswith('INFO:werkzeug:'):
        updatehttpevt(thisline)
        return
    elif thisline.startswith('WARNING:werkzeug:'):
        updatehttpevt(thisline)
        return
    elif thisline.startswith('ERROR:werkzeug:'):
        updatehttpevt(thisline)
        return
    elif thisline.startswith('CRITICAL:werkzeug:'):
        updatehttpevt(thisline)
        return
    else:
        print("Send to application monitoring function, write info messages to log, generate alerts on the higher severity")
        print(thisline)
        updatesecevt(thisline)

    return


def followfile(applog):
    # File seek ?
    applog.seek(0, os.SEEK_END)

    while True:
        thisline = applog.readline()
        #sleep 200 milliseconds
        if not thisline:
            time.sleep(0.2)
            continue
        # Functions normally return but yield can provide data from a function without needed to be called over and over
        # This seems to be referred to as a generator, perhaps a pattern
        yield thisline


if __name__ == '__main__':
    applogfile = open("/var/tmp/sfrdev.log","r")
    loglines = followfile(applogfile)

    for line in loglines:
        filterline(line)

