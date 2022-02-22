#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 18/2022 - Config file to avoid hardcoding settings in main file.  Make application more portable
#                   
#
# Notes: Initializes the flash application context
# https://hackersandslackers.com/flask-application-factory/
 
#######################################################################################################################
from flask.app import Flask
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir,'.env'))


TESTING=True
DEBUG=True
FLASK_ENV='development'
SECRET_KEY=environ.get('SECRET_KEY')