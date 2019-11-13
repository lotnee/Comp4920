from app import app
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
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
	# firstName = StringField('First Name', validators=[DataRequired()])
	# lastName = StringField('Last Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign Up')

class ProfileForm(FlaskForm):
	firstName = StringField('First Name', validators=[DataRequired()])
	lastName = StringField('Last Name', validators=[DataRequired()])
	descriptions = StringField('Descriptions', validators=[DataRequired()])
	gender = StringField('Gender', validators=[DataRequired()])
	# pictureDir = FileField(validators=[FileRequired('File empty :('), FileAllowed(photos, 'image only')])
	pictureDir = FileField(validators=[FileAllowed(photos, 'image only')])
	submit = SubmitField('Edit Profile')

class EventForm(FlaskForm):
	name  = StringField('Name', validators=[DataRequired()],render_kw = {"placeholder": "Enter The Name Of Your Event"})
	description = StringField('Description', validators=[DataRequired()], render_kw = {"placeholder": "Enter A Short Description Of Your Event"})
	submit = SubmitField('Create Event')
	start = DateField('Enter Your Start Date', format='%Y-%m-%d')
	end = DateField('When Does The Event End', format='%Y-%m-%d')
	#FIXME add start time and end time as string field
	pictureDir = FileField(validators=[FileAllowed(photos, 'image only')])