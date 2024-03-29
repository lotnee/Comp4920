from app import app, absolute_path
from app.database import DB
from app.models.profile import Profile
from app.controllers.forms import ProfileForm, photos
from app.utility.utility import get_cursor, get_list_of_documents
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
# from werkzeug.utils import secure_filename
from bson.json_util import dumps
from bson.objectid import ObjectId
import os

@app.route('/dashboard')
@login_required
def dashboard():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))

	incoming = DB.find(collection="Profile", query={"friends": {"$elemMatch": {"friend_id": user['_id'], "status": "pending"}}})
	requests = get_cursor(cursor_obj=incoming, key="friends", subkey="friend_id", subkey2="status", query=user['_id'], query2="pending")
	
	allEvents = []
	allPolls = []
	myEvents = []
	# if DB.find_one(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}}):
	if user['events'] != []:
		for event_id in user['events']:
			event = DB.find_one(collection='Events', query={'_id': event_id})
			event_host = DB.find_one(collection='Profile', query={'_id': event['host']})
			if user['_id'] == event_host['_id']:
				myEvents.append(event)
			else:
				allEvents.append({'_id': event['_id'],'name': event['name'], 'host': event_host['firstName'] + ' ' + event_host['lastName'], 'start': event['start'], 'end': event['end'], 'description': event['description'], 'pictureDir': event['pictureDir']})
		# allEvents = get_list_of_documents(obj_id_list=user['events'], collection='Events')
	# if DB.find_one(collection="Profile", query={"email":current_user.email, "polls": {"$ne" : []}}):
	if user['polls'] != []:
		allPolls = get_list_of_documents(obj_id_list=user['polls'], collection='Poll')
	return render_template('dashboard.html', title='Dashboard', polls = allPolls, myEvents=myEvents, invEvents=allEvents, me=user, requests=requests)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = ProfileForm()
	profile = DB.find_one(collection="Profile", query={"email": current_user.email})
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
				# credit: default female and male image from w3schools.com
				if form.pictureDir.data is None:
					if form.gender.data == "male":
						filename = "male.jpg"
					else:
						filename = "female.jpg"
				else:
					filename = photos.save(form.pictureDir.data, name= 'profile/' + user['email'] + '.')
					filename = filename.split('/')[1]
				profile_obj = Profile(email=user['email'], firstName=form.firstName.data, lastName=form.lastName.data, descriptions=form.descriptions.data, gender=form.gender.data, pictureDir=filename)
				profile_obj.insert()
			else:
				# update existing profile
				# Don't need to check if None since it is required in form
				# if form.firstName.data is not None:
				DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"firstName": form.firstName.data}})
				# if form.lastName.data is not None:
				DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"lastName": form.lastName.data}})
				# if form.descriptions.data is not None:
				DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"descriptions": form.descriptions.data}})
				# if form.gender.data is not None:
				DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"gender": form.gender.data}})
				if form.pictureDir.data is not None:
					if profile['pictureDir'] == "male.jpg" or profile['pictureDir'] == "female.jpg":
						filename = photos.save(form.pictureDir.data, name='profile/' + current_user.email + '.')
						filename = filename.split('/')[1]
					else:
						# delete existing photo
						filename = "app/static/images/profile/" + profile['pictureDir']
						os.remove(os.path.join(filename))
						filename = photos.save(form.pictureDir.data, name='profile/' + current_user.email + '.')
						filename = filename.split('/')[1]
					DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"pictureDir": filename}})
				else:
					if profile['pictureDir'] == "male.jpg" or profile['pictureDir'] == "female.jpg":
						filename = form.gender.data + ".jpg"
						DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"pictureDir": filename}})

		return redirect('/profile')

	return render_template('edit-profile.html', title='Edit profile', form=form, profile=profile)

@app.route('/profile/<profile_id>')
@login_required
def profile(profile_id,is_profile_owner=False):
	user = DB.find_one(collection="Profile", query={'_id':
		ObjectId(profile_id)})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))

	me = DB.find_one(collection="Profile", query={"email":
		current_user.email})

	def are_we_friends(entry):
		return (entry['friend_id'] == me['_id'] 
				and entry['status'] == 'accepted')
	is_friend = any(filter(are_we_friends, user['friends']))
	eventList = []
	for events in user['events']:
		events = DB.find_one(collection='Events', query={'_id': events})
		if not events:
			continue
		event_dict = {'title': events['name'], 
				'start': events['start'].strftime("%Y-%m-%d"), 
				'end': events['end'].strftime("%Y-%m-%d")}
		eventList.append(event_dict)
	if not eventList:
		eventList = {}

	return render_template('profile.html', profile=user,
				events=eventList,
				is_profile_owner=is_profile_owner,
				is_friend=is_friend)

@app.route('/profile')
@login_required
def my_profile():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))

	return profile(str(user['_id']),is_profile_owner=True)
