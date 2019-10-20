from app import app
from app.database import DB
from app.models.user import User
from app.models.profile import Profile
from app.models.events import Event
from app.controllers.forms import LoginForm, RegistrationForm, ProfileForm, photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html')

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = DB.find_one(collection="User", query={"email": form.email.data})
		if user and check_password_hash(user['password'], form.password.data):
			user_obj = User(email=user['email'], password=user['password'])
			# print(user_obj.email)
			login_user(user_obj)
			# flash(user_obj.name)
			return redirect(url_for('dashboard'))
			# next_page = request.args.get('next')
			# if not next_page or url_parse(next_page).netloc != '':
			#     next_page = url_for('index')
			# return redirect(next_page)
		else:
			flash("Invalid email or password")
	return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = DB.find_one(collection="User", query={"email": form.email.data})
		if user is None:
			user_obj = User(email=form.email.data, password=generate_password_hash(form.password.data))
			user_obj.insert()
			login_user(user_obj)
			return redirect(url_for('edit_profile'))
		else:
			flash("Invalid email")
	return render_template('registration.html', title='Sign Up', form=form)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = ProfileForm()
	if form.validate_on_submit():
		user = DB.find_one(collection="User", query={"email": current_user.email})
		if user is None:
			flash("Sign Up Failed")
			return redirect(url_for('register'))
		else:
			profile = DB.find_one(collection="Profile", query={"email": user['email']})
			if profile is None:
				# https://pythonise.com/feed/flask/flask-uploading-files
				# can possibly add more checks (e.g. file extension)
				# can't seem to get secure_filename() to work
				# file = secure_filename(form.pictureDir.data.filename)
				# file = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file)
				# print(file)
				filename = photos.save(form.pictureDir.data, name=user['email'] + '.')
				# print(filename)
				# fileDest = photos.path(filename)
				# print(fileDest)

				profile_obj = Profile(email=user['email'], name=form.name.data, descriptions=form.descriptions.data, gender=form.gender.data, pictureDir=filename)
				profile_obj.insert()
				# TODO database aggregation
				# DB.aggregate(collection="User", query=[{"$lookup":{"from":"Profile", "localField":"email", "foreignField":"email", "as":"user_profile"}}])
			#  else:
				# TODO update existing profile
		return redirect(url_for('profile'))
	return render_template('edit-profile.html', title='Edit profile', form=form)

@app.route('/profile')
@login_required
def profile():
	return render_template('profile.html')

@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
	form = EventForm()
	if form.validate_on_submit():
		print(type(form.start.data))
		date1 = datetime((form.start.data).year,(form.start.data).month,(form.start.data).day)
		date2 = datetime(2011, 11, 4, 0, 0)
		print("start date is " + date1.isoformat())
		event = Event(name = form.name.data, description = form.description.data, start = date1, end = date2)
		event.insert()
		return "hehe"
	return render_template('events.html', title = "Create Your Event", form = form)
