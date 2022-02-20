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
def present_files():
    # read files from database    
    SQLGETLIST = ''' SELECT id,filename from blobsbx WHERE filebin IS NOT NULL  '''
    try:
        thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
        thiscur=thisdbh.cursor()
        result=thiscur.execute(SQLGETLIST)
        # get top ten records
        recordstuple = thiscur.fetchmany(size=10)
        print(recordstuple)
        thisdbh.close()
    except Exception as err:
        print(err)
    return   


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'upfile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        newfile = request.files['upfile']
        keywords = request.form['keytag']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if newfile.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if newfile and allowed_file(newfile.filename):
            flash('File uploaded' )
            upfilename = secure_filename(newfile.filename) # werkzueg built in function to deal with escape paths
            upfilebytes = newfile.stream.read()  # assuming this is a byte stream
            UPLOADSQL = ''' INSERT INTO blobsbx (filename,filebin) VALUES (%s,%s) '''
            print(type(upfilebytes)) 
            print(len(upfilebytes))
            print(upfilename)
            print(str(keywords))
            # Write file to database
            try:
                thisdbh=tbsnippets.sbxdbconnect('10.100.200.3','sbxuser','someP@SSwerd','tbsbx')
                thiscur=thisdbh.cursor()
                result=thiscur.execute(UPLOADSQL, (upfilename,upfilebytes))
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
    app.run(host="0.0.0.0",port=8889, debug=True)