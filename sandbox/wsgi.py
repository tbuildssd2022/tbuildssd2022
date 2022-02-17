#!/bin/env python3

from flask import Flask
app = Flask(__name__)
app.config['FLASK_ENV'] =  'development'
#app.config['DEBUG'] = True
# Never do this in production, seriously never do this
app.config['SECRET_KEY'] = 'TH!Sis@v3ryl0ngkeyTH@Tisn0ts3cr3t'



@app.route("/")
def hello_flask():
    return "<p>Hello, flask 101 place holder</p>"

@app.route("/test", defaults={'prm': None})
@app.route("/test/<prm>")
def testit(prm):
    if not prm:
        return "<p>testing, no param passed</p>"
    else:    
        return "<p>testing, param passed: {} </p>".format(prm)



if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8443, debug=True)

