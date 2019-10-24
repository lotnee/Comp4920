from app import app
from app.database import DB
from app.models.user import User
from app.models.profile import Profile
from app.models.events import Event
from app.models.friend import Friend
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
		print(form.pictureDir.data)
		user = DB.find_one(collection="User", query={"email": current_user.email})
		# a question about the code below: shouldn't we determine whether the user managed to sign up first in the registration page, and then if
		# user doesn't succeed, they are unable to log in to edit their profile? or am i misunderstanding it ahaha
		# ^ hi to answer your question, i assume you are a front end dev
		# how the registration works is if you successfully sign up, you will be automatically logged in.
		# if failed obviously can't even edit profile
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
				if form.pictureDir.data is None:
					if form.gender.data == "male":
						filename = "male.jpg"
					else:
						filename = "female.jpg"
				else:
					filename = photos.save(form.pictureDir.data, name=user['email'] + '.')
				# print(filename)
				# fileDest = photos.path(filename)
				# print(fileDest)

				profile_obj = Profile(email=user['email'], firstName=form.firstName.data, lastName=form.lastName.data, descriptions=form.descriptions.data, gender=form.gender.data, pictureDir=filename)
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
	profile = DB.find_one(collection="Profile", query={"email": current_user.email})
	return render_template('profile.html', profile=profile)

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

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
	users = list(DB.find_all(collection="Profile"))
	me = DB.find_one(collection="Profile", query={"email": current_user.email}) 
	requests = DB.find(collection="Profile", query={"friends.email": current_user.email, "friends.status":"pending"})
	return render_template('friend.html', title='Friend List', users=users, me=me, requests=requests)

@app.route('/send-request/<email>')
@login_required
def send_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"friends.email": email})
	if added is not None:
		flash('Request to %s sent!' % email)
		return redirect(url_for('friends'))
	friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="pending")
	friend_obj.insert(current_user.email)
	flash('Friend request sent to ' + email + '!')
	return redirect(url_for('friends'))

@app.route('/delete-request/<email>')
@login_required
def delete_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"friends.email": email})
	added2 = DB.find_one(collection="Profile", query={"friends.email": current_user.email})
	# added = DB.find_one(collection="Profile", query={"friends": {"$elemMatch": {"email": email} }})
	# print(added['friends'][0]['email']) 
	# ^ LMAO can't seem to convert list to dict and i found this way works so ...
	if added is not None and added['friends'][0]['status'] == "pending":
		friend_obj = Friend(email=added['friends'][0]['email'], firstName=added['friends'][0]['firstName'], lastName=added['friends'][0]['lastName'], status=added['friends'][0]['status'])
		friend_obj.remove(current_user.email)
		flash('Friend request ' + email + ' cancelled!')
	elif added2 is not None and added2['friends'][0]['status'] == "pending":
		friend_obj2 = Friend(email=added2['friends'][0]['email'], firstName=added2['friends'][0]['firstName'], lastName=added2['friends'][0]['lastName'], status=added2['friends'][0]['status'])
		friend_obj2.remove(email)
		flash('Friend request ' + email + ' rejected!')
	elif added and added2 is not None: 
		friend_obj = Friend(email=added['friends'][0]['email'], firstName=added['friends'][0]['firstName'], lastName=added['friends'][0]['lastName'], status=added['friends'][0]['status'])
		friend_obj.remove(current_user.email)
		friend_obj2 = Friend(email=added2['friends'][0]['email'], firstName=added2['friends'][0]['firstName'], lastName=added2['friends'][0]['lastName'], status=added2['friends'][0]['status'])
		friend_obj2.remove(email)
		flash('Friend request ' + email + ' deleted!')
	else:
		flash('No such request to %s!' % email)
	return redirect(url_for('friends'))

@app.route('/accept-request/<email>')
@login_required
def accept_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"friends.email": current_user.email, "friends.status": "pending"})
	if added is not None:
		DB.update_one(collection="Profile", filter={"friends.email": current_user.email}, data={"$set": {"friends.0.status": "accepted"}})
		friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="accepted")
		friend_obj.insert(current_user.email)
		flash('Accepted %s\'s friend request!' % email)
		return redirect(url_for('friends'))
	flash('%s is already a friend' % email)
	return redirect(url_for('friends'))