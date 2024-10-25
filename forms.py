from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileRequired, FileAllowed, FileSize

class RegistrationForm(FlaskForm):

    username = StringField('Username:', validators = [DataRequired(), Length(min = 3, max = 20)])
    email = StringField('Email address:', validators = [DataRequired(), Email()])
    password = PasswordField('Password:', validators = [DataRequired(), Length(min = 6)])
    password_confirm = PasswordField('Confirm Password:', validators = [DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):

    email = StringField('Email address:', validators = [DataRequired(), Email()])
    password = PasswordField('Password:', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UploadForm(FlaskForm):

    name = StringField('File name:', validators = [DataRequired(), Length(min = 3, max=120)])
    file = FileField('Select file:', validators = [FileRequired(), FileSize(max_size = 20 * 1024 * 1024), FileAllowed(['stl'], 'Only .stl files are allowed.')])
    desc = TextAreaField('Description:', validators = [Length(max = 1000)])
    private = BooleanField('Private (invisible on the home page)')
    submit = SubmitField('Upload')

class DetailForm(FlaskForm):

    delete = SubmitField('Delete')
    download = SubmitField('Download')
    private = BooleanField('Private (invisible on the home page)')
    submit = SubmitField('Save')