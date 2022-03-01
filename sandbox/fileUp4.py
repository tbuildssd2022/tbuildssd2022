#!/bin/env python3
# Author(s): Doug Leece
# Version history: Feb 19/2022 - Initial creation
# 
# Notes: Development version needed to work out file transfer requirements. 
# Extended the example pattern provided by Flask maintainers:
# https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
# 
#######################################################################################################################

from crypt import methods
import mimetypes, os, io, tbsnippets
from tbsnippets import getcurdate

from flask import Flask, flash, request, redirect, url_for, send_file
from flask import send_from_directory
from werkzeug.utils import secure_filename
import logging


UPLOAD_FOLDER = '/var/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf','doc','docx','png', 'jpg', 'jpeg', 'gif','zip','gz','tar'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']= 32 * 1000 * 1024
app.config['FLASK_ENV'] =  'production'
app.config['DEBUG'] = False
# Never do this in production, seriously never do this
app.config['SECRET_KEY'] = 'TH!Sis@v3ryl0ngkeyTH@Tisn0ts3cr3t'
#
# Modify Flask's built-in incorporation of the Python logging library.
# Set the logging level down to debug to allow troubleshooting of conditions.
# Write operational events to the info facility - severity 20
# Write security events to the warning facility - severity 30
logging.basicConfig(filename= '/var/tmp/sfrsbx.log', level=logging.DEBUG)

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# List files in the database
@app.route('/flist', methods=['GET'])
def search_files():
    app.logger.info('Inside flist route - search_files')
    return '''
    <!doctype html>
    <title>Search existing files</title>
    <h1>Search for files in database</h1>
    <form action="flist2" method=post enctype=multipart/form-data>
      <p>&nbsp</p>
      <p> Search for Keyword or tags, ( single term only) 
      <input type=text name=keytag> </p>
      <p>&nbsp</p>
      <p> Search for filename or partial filename , ( single term only) 
      <input type=text name=filename> </p>
      <p>&nbsp</p>
      <input type=submit value=search>
    </form>
    '''

  
@app.route('/flist2', methods=['POST'])
def present_files():
    app.logger.info('Inside flist2 route - present_files')
    searchkey = request.form.get('keytag')
    searchfname = request.form.get('filename')
    print(len(searchkey))
    print(len(searchfname))
    SQLGETLIST1 = "select filename,keywords_tags,filetype,filesize,filecreate,fileowner,uuid_hex from storedfiles WHERE filename like '%{}%'".format(searchfname)
    SQLGETLIST2 = "select filename,keywords_tags,filetype,filesize,filecreate,fileowner,uuid_hex from storedfiles WHERE keywords_tags like '%{}%'".format(searchkey)
    #SQLGETLIST = "select filename,keywords_tags,filetype,filesize,filecreate,fileowner,uuid_bin from storedfiles WHERE filename like '%{}%'".format(search)
    #SQLGETLIST = "SELECT filename,keywords_tags from storedfiles WHERE filename like '%{}%'".format(search)
    print(SQLGETLIST1)
    print(SQLGETLIST2)
    if (len(searchfname) > 0) and (len(searchkey)== 0):
        SQLGETLIST = SQLGETLIST1
    elif (len(searchfname) == 0) and (len(searchkey) > 0 ):
        SQLGETLIST = SQLGETLIST2
    else:
        # Collect the exception thrown if the connection fails for any reason
        payloadlist=['UXReport','search failure','keytag',searchkey,'filename',searchfname]
        logmsgdict = tbsnippets.newlogheader(1,0,0,99)  # faking user 99
        logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
        app.logger.info(logmsg)
        return'''
        <!doctype html>
            <title>List Database Files -error </title>
            <h1>That didn't quite work :-( </h1>
            <p> You need to include either a partial file name or partial keyword to return a file list <br>
            <a href="/"> Return to File upload </a> </p>
        '''
        
    # Run the search for either partial filename or partial keyword
    try:
        thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
        thiscur=thisdbh.cursor()
        result=thiscur.execute(SQLGETLIST)
        # get top ten records
        recordstuple = thiscur.fetchmany(size=10)
        print(recordstuple)
        thisdbh.close()
        return '''
            <!doctype html>
            <title>List Database Files </title>
            <h1>Jinga Template parsing next</h1>
            <p> Some kind of file list generated <br>
            <a href="/"> Return to File upload </a> </p>
            '''
    except Exception as err:
        print(err)
        # Collect the exception thrown if the connection fails for any reason
        payloadlist=['DBError',err]
        logmsgdict = tbsnippets.newlogheader(3,3,8,99)  # faking user 99
        logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
        app.logger.error(logmsg)
        return '''
            <!doctype html>
            <title>List Database Files - Error</title>
            <h1>Jinga Template parsing next</h1>
            <p> Some kind of database error generated <br>
            <a href="/"> Return to File upload </a> </p>
            '''

# Select a file to download from the database
@app.route('/fdl1', methods=['GET'])
def select_file_download():
    app.logger.info('Inside fdl11 route - file_downlload')
    return '''
    <!doctype html>
    <title>Download existing files</title>
    <h1>Download a file from database</h1>
    <form action="fdl7" method=post enctype=multipart/form-data>
      <p>&nbsp</p>
      <p> File UUID, ( single file ) 
      <input type=text name=fileid> </p>
      <p>&nbsp</p>
      <input type=submit value=download>
    </form>
    '''


@app.route('/fdl7', methods=['GET','POST'])
def download_file2():
    if request.method == 'GET':
        # record someone is downloading a file, collect the fileid, filename and userid"
        payloadlist=['URL','/fdl17','method',request.method]
        logmsgdict = tbsnippets.newlogheader(2,2,0,99)  # faking user 99
        logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
        app.logger.warning(logmsg)
        return '''
         <!doctype html>
            <title>Download database Files - Error</title>
            <h1> Only post requests supported</h1>
            <p> You also need the uuid_hex value for the file <br>
            <a href="/"> Return to File upload </a> </p>
        '''
    if request.method == 'POST':
        # We need to test this to make sure it's a valid UUID hex value
        uuid_hex = request.form['fileid']
        SQLFILEDOWNLOAD= "SELECT filename,filetype,filesize,filedata from storedfiles WHERE uuid_hex='{}'".format(uuid_hex)
        # Run the search for either partial filename or partial keyword
        try:
            thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
            thiscur=thisdbh.cursor()
            result=thiscur.execute(SQLFILEDOWNLOAD)
            # get file meta data needed for download and the file data stored as bytes in the database
            recordstuple = thiscur.fetchone()
            print(recordstuple[0])
            print(recordstuple[1])
            print(recordstuple[2])
            print(len(recordstuple[3]))
            fileblob=io.BytesIO(recordstuple[3])  # Convert the byte array into something send-file can read
            filename=recordstuple[0]
            filetype=recordstuple[1]   # This should be sent to a function that creates the correct mime type
            thisdbh.close()
            # record someone is downloading a file, collect the fileid, filename and userid"
            payloadlist=['FileId',uuid_hex,'FileName',filename]
            logmsgdict = tbsnippets.newlogheader(1,1,6,99)  # faking user 99
            logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
            app.logger.info(logmsg)

            # Need to process the first three data elements to define the response header? ( depends on send_file)
            # hard coding as text/pain for now
            return send_file(fileblob, as_attachment = True, download_name=filename, mimetype = 'text/plain')


        except Exception as err:
            print(err)
            # Collect the exception thrown if the connection fails for any reason
            payloadlist=['DBError',err]
            logmsgdict = tbsnippets.newlogheader(3,3,8,99)  # faking user 99
            logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
            app.logger.error(logmsg)
            return '''
                <!doctype html>
                <title>Download Database Files - Error</title>
                <h1>Check the database connection?</h1>
                <p> Some kind of database error generated <br>
                <a href="/"> Return to File upload </a> </p>
            '''
    



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # record someone accessed the URL, no additional info but we can collect the URL & method"
    payloadlist=['URL','/','method',request.method]
    logmsgdict = tbsnippets.newlogheader(1,0,0)
    logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
    app.logger.info(logmsg)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'upfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        newfile = request.files['upfile']
        #keywords = request.form.get('keytag',None)  # Test for missing value since this is an optional field
        keywords = request.form['keytag']
        fileowner = request.form['uid']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if newfile.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if newfile and allowed_file(newfile.filename):
            flash('File uploaded' )
            filename = secure_filename(newfile.filename) # werkzueg built in function to deal with escape paths
            filedata = newfile.stream.read()  # assuming this is a byte stream
            filesize = len(filedata) # An array of bytes easily counted at insert,  useful meta data going forward
            filetype = filename.rsplit('.', 1)[1].lower() # Force to lowercase for simplified searching
            dtcreate = tbsnippets.getcurdate()
            fileuuid = tbsnippets.getnewuuid()
            
            # Define a searchable value for system maintenance 
            #if keywords is None:
            #    keywords='no_keywords'
            #    print(str(keywords))
            # Required fields + keywords. 
            UPLOADSQL = ''' INSERT INTO storedfiles(uuid_hex,filename,filetype,filedata,fileowner,filecreate,filesize,keywords_tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) '''
            VALUESTUPLE = (fileuuid,filename,filetype,filedata,fileowner,dtcreate,filesize,keywords)
            # Each critical section should have a developed function to track the specific additional data that should be included
            # create as a list so it is easy to load this into the dictionary. Ensure everything is cast as strings  
            payloadlist = ['FileID',fileuuid,'FileName',filetype,'FileOwner',str(fileowner),'FileCreateDate',str(dtcreate),'FileSize',str(filesize),'keywords',keywords[:60]]
            
            logmsgdict=tbsnippets.newlogheader(2,1,7,int(fileowner))
            logmsg=tbsnippets.newlogmsg(logmsgdict,payloadlist)
            app.logger.warning(logmsg)
            # Write file to database
            try:
                thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
                thiscur=thisdbh.cursor()
                result=thiscur.execute(UPLOADSQL, VALUESTUPLE)
                thisdbh.commit()
                thisdbh.close()
            except Exception as err:
                print(err)
            
            return redirect(request.url)
            #return redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File to database</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=upfile>
      <p>&nbsp</p>
      <p> User ID int value - Use 2, 5 or 17  
      <input type=text name=uid> </p>
      <p>&nbsp</p>
      <p> Keywords or tags 
      <input type=text name=keytag> </p>
      <p>&nbsp</p>
      <input type=submit value=Upload>
    </form>
    <p>&nbsp </p>
    <p> View currently stored files SFR database. <br>
    <a href="/flist"> File list </a> </p>

    '''


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080, debug=True)