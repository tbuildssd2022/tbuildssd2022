#!/bin/env python3
# Author(s): Doug Leece
# Version history: Mar 1/2022 - Initial creation
#
# Attempting to keep this native python instead of OS specific shelling out to tail -f
# Starting with this : https://medium.com/@aliasav/how-follow-a-file-in-python-tail-f-in-python-bca026a901cf
#
################################################################################################################
import time, os, datetime, re, json
# using third party library for syslog transport
import pysyslogclient

from ast import literal_eval  # a safe way to convert the string to a dictionary

################################  Log File Management ###################################
# These function receive event logs of all severity and write to a daily file, 
# converting the werkzeug events into HTTP NCSA format and the custom application
# security event log into json.

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

#############################  Remote Logging Transport ##########################################
# This function creates a syslog client for transporting the log messages to the ground station 
# security monitoring solution
def newsyslogclient(hostipstr):
    slogclient= pysyslogclient.SyslogClientRFC3164(hostipstr,601,proto="TCP")
    return slogclient

# This function crafts the event log into a syslog formatted message
# then sends the message to a remote syslog server
def setremotealert(secevtline):
    prog='sfralerting'
    logtransport=newsyslogclient('10.100.200.3')
    logtransport.log(secevtline,facility=pysyslogclient.FAC_SECURITY,severity=pysyslogclient.SEV_WARNING,
    program=prog,pid=4242)
    logtransport.close()
    return



#################################  Log Event Filtering ###########################################

# this function evaluates the application log, forwarding warning events and higher
# to the ground station security monitoring.  Informational messages are just forwaded to
# the daily logfile since the do reflect a potential cybersecurity or application usage
# issue and will be a waste of bandwidth.
# 
def testsecevt(secevtline):
    print(secevtline)
    if secevtline.split(':')[0]=="INFO":
        updatesecevt(secevtline)
    else:
        print("realtime alert")
        updatesecevt(secevtline)
        setremotealert(secevtline)
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
        testsecevt(thisline)
    return

# This function, is the core enabler of this monitoring program. It creates a "generator" that continuously monitors the Flask logging output
# and sends new event log lines into the monitoring program. The pattern uses yield rather 
# than the typical function return, allowing the continous output of line data without having
# to recall the function over an over.  
# https://wiki.python.org/moin/Generators 

def followfile(applog):
    # File seek ?
    applog.seek(0, os.SEEK_END)

    while True:
        thisline = applog.readline()
        #sleep 200 milliseconds
        if not thisline:
            time.sleep(0.2)
            continue
        yield thisline


if __name__ == '__main__':
    applogfile = open("/var/tmp/sfrdev.log","r")
    loglines = followfile(applogfile)

    for line in loglines:
        filterline(line)

