#!/bin/env python3
# Author(s): Doug Leece
# Version history: Mar 1/2022 - Initial creation
#
# Attempting to keep this native python instead of OS specific shelling out to tail -f
# Starting with this : https://medium.com/@aliasav/how-follow-a-file-in-python-tail-f-in-python-bca026a901cf
#
################################################################################################################
import time, os

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





def filterline(thisline):
    # test first to see if we get the lines, then start analysing
    #print(type(thisline))
    # filter out the werkzueg logs, and potentially clean them up to look like standard W3C logs
    # Using a case statement instead of regex for speed
    if thisline.startswith('INFO:werkzeug:'):
        print("send to http log formater")
        return
    elif thisline.startswith('WARNING:werkzeug:'):
        print("send to http log formater")
        return
    elif thisline.startswith('ERROR:werkzeug:'):
        print("send to http log formater")
        return
    elif thisline.startswith('CRITICAL:werkzeug:'):
        print("send to http log formater")
        return
    else:
        print("Send to application monitoring function")
        print(thisline)
    return


if __name__ == '__main__':
    applogfile = open("/var/tmp/sfrdev.log","r")
    loglines = followfile(applogfile)

    for line in loglines:
        filterline(line)

