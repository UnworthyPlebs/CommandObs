from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, URLField, IntegerField
from wtforms.validators import DataRequired, Length, equal_to, EqualTo, Regexp
from flask import request
from urllib.parse import urlparse, urljoin

class SignupForm(FlaskForm):
    username =  StringField('Username', validators=[DataRequired(), Length(min = 4, max = 20), Regexp(r'^\S+$', message="Username must not contain spaces.")])
    password = PasswordField('Password', validators=[DataRequired(), Regexp(r'^\S+$', message="Password must not contain spaces."), Length(min = 7)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username =  StringField('Username', validators=[DataRequired(), Length(min = 4, max = 20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class createInstance(FlaskForm):
    name =  StringField('Name', validators=[DataRequired(), Length(min = 4, max = 20)])
    host = StringField('URL', validators=[DataRequired()])
    password = PasswordField('Instance password', validators=[DataRequired(), Regexp(r'^\S+$', message="Password must not contain spaces."), Length(min = 4)])
    submit = SubmitField('Connect to OBS')




def is_safe_url(target):
    if not target:
        return True
    
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
