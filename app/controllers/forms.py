from app import app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app) # default image size 16MB

class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
   firstname = StringField('First Name', validators=[DataRequired()])
   lastname = StringField('Last Name', validators=[DataRequired()])
   email = StringField('Email', validators=[DataRequired()])
   password = PasswordField('Password', validators=[DataRequired()])
   submit = SubmitField('Sign Up')

class ProfileForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	descriptions = StringField('Descriptions', validators=[DataRequired()])
	gender = StringField('Gender', validators=[DataRequired()])
	pictureDir = FileField(validators=[FileRequired('File empty :('), FileAllowed(photos, 'image only')])
	submit = SubmitField('Edit Profile')

