#!/bin/env python3
import os
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import tbsnippets

UPLOAD_FOLDER = '/var/tmp/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf','doc','docx','png', 'jpg', 'jpeg', 'gif','zip','gz','tar'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH']= 32 * 1000 * 1024
app.config['FLASK_ENV'] =  'development'
#app.config['DEBUG'] = True
# Never do this in production, seriously never do this
app.config['SECRET_KEY'] = 'TH!Sis@v3ryl0ngkeyTH@Tisn0ts3cr3t'


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# List files in the database
@app.route('/flist', methods=['GET'])
def search_files():
    return '''
    <!doctype html>
    <title>Search existing files</title>
    <h1>Search for files in database</h1>
    <form action="flist2" method=post enctype=multipart/form-data>
      <p>&nbsp</p>
      <p> Search for Keyword or tags, ( single term only) 
      <input type=text name=keytag> </p>
      <p>&nbsp</p>
      <input type=submit value=search>
    </form>

    '''


    
    # read files from database    
    #SQLGETLIST = ''' SELECT id,filename from blobsbx WHERE filebin IS NOT NULL  '''
   
  
@app.route('/flist2', methods=['POST'])
def present_files():
    search = request.form.get('keytag')
    SQLGETLIST = "select filename,keywords_tags,filetype,filesize,filecreate,fileowner,uuid_hex from storedfiles WHERE filename like '%{}%'".format(search)
    #SQLGETLIST = "select filename,keywords_tags,filetype,filesize,filecreate,fileowner,uuid_bin from storedfiles WHERE filename like '%{}%'".format(search)
    #SQLGETLIST = "SELECT filename,keywords_tags from storedfiles WHERE filename like '%{}%'".format(search)
    print(search)
    print(SQLGETLIST)
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
        return '''
            <!doctype html>
            <title>List Database Files - Error</title>
            <h1>Jinga Template parsing next</h1>
            <p> Some kind of database error generated <br>
            <a href="/"> Return to File upload </a> </p>
            '''


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'upfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        newfile = request.files['upfile']
        keywords = request.form.get('keytag',None)  # Test for missing value since this is an optional field
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
            if keywords is None:
                keywords='no_keywords'
                print(str(keywords))
            # Required fields + keywords. 
            UPLOADSQL = ''' INSERT INTO storedfiles(uuid_hex,filename,filetype,filedata,fileowner,filecreate,filesize,keywords_tags) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) '''
            VALUESTUPLE = (fileuuid,filename,filetype,filedata,fileowner,dtcreate,filesize,keywords)
            
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
    app.run(host="0.0.0.0",port=8990, debug=True)