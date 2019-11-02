from app import app
from app.database import DB
from app.models.profile import Profile
from app.models.friend import Friend
from app.controllers.forms import ProfileForm, photos
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import os

def profileEvents(eventLists):
	retList = []
	for item in eventLists:
		event = DB.find_one(collection="Events",query={'_id':item})
		retList.append(event)
	print(retList[0]['name'])
	return retList
@app.route('/dashboard')
@login_required
def dashboard():
	if DB.find_one(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}}):
		print("penis")
		eventList = DB.find(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}})
		print(eventList[0]['events'])
		allEvents = profileEvents(eventList[0]['events'])
		return render_template('dashboard.html', events = allEvents)
	return render_template('dashboard.html')

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = ProfileForm()
	profile = DB.find_one(collection="Profile", query={"email": current_user.email})
	if form.validate_on_submit():
		# print(form.pictureDir.data)
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
				# credit: default female and male image from w3schools.com
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
			else:
				# update existing profile
				# DOn't really need to check if None since it is required
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
						filename = photos.save(form.pictureDir.data, name=current_user.email + '.')
					else:
						# delete existing photo
						filename = "app/static/images/" + profile['pictureDir']
						os.remove(os.path.join(filename))
						filename = photos.save(form.pictureDir.data, name=current_user.email + '.')
					DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"pictureDir": filename}})
				else:
					if profile['pictureDir'] == "male.jpg" or profile['pictureDir'] == "female.jpg":
						filename = form.gender.data + ".jpg"
						DB.update_one(collection="Profile", filter={"email": current_user.email}, data={"$set": {"pictureDir": filename}})

				# update all friend's model picture dir if changed
				toUpdateList = DB.find(collection="Profile", query={"friend": {"$elemMatch": {"email": current_user.email}}})
				i = 0
				while i < toUpdateList.count():
					j = 0
					while j < len(toUpdateList[i]['friend']):
						if toUpdateList[i]['friend'][j]['email'] == current_user.email:
							friend_pic = "friends." + str(j) + ".pictureDir"
							DB.update_one(collection="Profile", filter={"email": toUpdateList[i]['email']}, data={"$set": {friend_pic: filename}})
		
		return redirect(url_for('profile'))
	return render_template('edit-profile.html', title='Edit profile', form=form, profile=profile)

@app.route('/profile')
@login_required
def profile():
	profile = DB.find_one(collection="Profile", query={"email": current_user.email})
	return render_template('profile.html', profile=profile)
