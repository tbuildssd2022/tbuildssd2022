#!/bin/env python3
# Author(s): Doug Leece
# Version history:  Feb 26/2022 - Inital setup, Custom classes
#                   
#
# Notes: The WTF forms framwork requires classes. Certain simple forms may be possbile with this framework,
# simplifying validation measures.
# 
# Currently this is a single collection, group similar classes into commented sections to enable refactoring if
# the collection becomes too large.
 
#######################################################################################################################

# Flask specific wrapper for forms input validation
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField,PasswordField
from wtforms.validators import DataRequired, InputRequired

class loginForm(FlaskForm):
    wtfaid=StringField('ISS access ID (EG. EU123i45j)',validators=[DataRequired()])
    wtfpwd=PasswordField()

