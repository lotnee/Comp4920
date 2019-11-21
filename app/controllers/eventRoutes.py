from app import app
from app.database import DB
from app.models.events import Event
from app.models.friend import Friend
from app.controllers.forms import photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.utility.utility import get_list, get_cursor
from datetime import datetime, time
from bson.objectid import ObjectId
import json


def profileEvents(eventLists):
	retList = []
	for item in eventLists:
		event = DB.find_one(collection="Events",query={'_id':item})
		retList.append(event)
	return retList

@app.route('/create-event', methods=['GET', 'POST'])
@login_required
def create_events():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	form = EventForm()
	# if form.is_submitted():
	if form.validate_on_submit():
		me = DB.find_one(collection="Profile", query={"email": current_user.email})
		form.starttime.data = form.starttime.data.split(' ')
		time1 = form.starttime.data[0].split(':')
		if form.starttime.data[1] == 'PM':
			time1[0] = int(time1[0]) + 12
			if time1[0] == 24:
				time1[0] = 0
		time1 = time(int(time1[0]), int(time1[1]))

		form.endtime.data = form.endtime.data.split(' ')
		time2 = form.endtime.data[0].split(':')
		if form.endtime.data[1] == 'PM':
			time2[0] = int(time2[0]) + 12
			if time2[0] == 24:
				time2[0] = 0
		time2 = time(int(time2[0]), int(time2[1]))

		date1 = datetime((form.start.data).year,(form.start.data).month,(form.start.data).day, time1.hour, time1.minute)
		date2 = datetime((form.end.data).year,(form.end.data).month,(form.end.data).day, time2.hour, time2.minute)
		# check date and time
		if date1 < datetime.now():
			flash('Start has to be today or later!')
			return render_template('create-event.html', title = "Create Your Event", form = form)
		elif date2 < date1:
			flash('End cannot be earlier than Start!')
			return render_template('create-event.html', title = "Create Your Event", form = form)
		elif date1 == date2:
			flash('Start and End cannot be the same!')
			return render_template('create-event.html', title = "Create Your Event", form = form)
		if form.pictureDir.data is None:
			filename = "event.jpg"
		else:
			filename = photos.save(form.pictureDir.data, name= 'event/' + str(user['_id']) + '.')
			filename = filename.split('/')[1]
		# print(f'name: {form.name.data}')
		# print(f'description: {form.description.data}')
		# print(f'start: {date1}')
		# print(f'end: {date2}')
		# print(f'pictureDir: {filename}')
		# print(f'type {form.eventType.data}')
		form.name.data = form.name.data.strip()
		form.description.data = form.description.data.strip()
		if form.eventType.data == 'private':
			event = Event(name = form.name.data, description = form.description.data,
						  start = date1, end =date2,
						  host=me['_id'],
						  invitees=[], pictureDir=filename, private=True)
		else:
			event = Event(name = form.name.data, description = form.description.data,
						  start = date1, end =date2,
						  host=me['_id'],
						  invitees=[], pictureDir=filename, private=False)
		event.insert(current_user.email)
		return redirect(url_for('event_completed'))
	return render_template('create-event.html', title = "Create Your Event", form = form)

@app.route('/view-events')
@login_required
def view_events():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	if DB.find_one(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}}):
		eventList = DB.find(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}})
		allEvents = profileEvents(eventList[0]['events']) #FIXME doesn't seem right
		#what doesn't seem right?
		return render_template('events.html', events = allEvents, title='View Events')
	return render_template('events.html',title="View Events")

@app.route('/event-completed')
@login_required
def event_completed():
	return render_template('event-completed.html',title="Event Creation Completed")

@app.route('/view-events/<path:id>')
@login_required
def display_event(id):
	#get the event name or more so the ID
	eventDetails = DB.find_one(collection = "Events", query = {"_id":ObjectId(id)})
	# gets all the friends of the user
	retDictionary = DB.find_one(collection = "Profile", query = {"email":current_user.email})
	friends = retDictionary['friends']
	# remember to filter out only active friends, no pending but do it later
	return render_template('display-event.html', event = eventDetails, friends = json.dumps(friends))

@app.route('/delete-event/<string:id>')
@login_required
def delete_event(id):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	#delete the event from the id
	#first go through all the users that is associated with that id
	x = DB.find_one(collection="Events", query = {"_id":ObjectId(id)})
	print(x)
	profileList = x['invitees']
	print(profileList)
	# Delete the event from all users in profile
	for profile in profileList:
		DB.update_one(collection = "Profile", filter = {"email":profile['email']}, data = {"$pull": {"events" : ObjectId(id)}})
	#delete the actual event from the database
	DB.remove(collection = "Events", condition = {"_id": ObjectId(id)})
	return redirect(url_for("view_events"))

# for poll
@app.route('/create-event/<poll>', methods=['GET', 'POST'])
@login_required
def poll_create_event(poll):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	my_poll = DB.find_one(collection="Poll", query={"_id": ObjectId(poll)})
	if my_poll is None:
		flash('Please contact admin, DB issues!')
		return redirect(url_for('polls'))
	for option in my_poll['options']:
		print(option)
		if 'voters' in option:
			for voter in option['voters']:
				print(voter)
				if voter == user['firstName']:
					date1 = option['date']

	event_obj = Event(name=my_poll['name'] , description =
			my_poll['description'], start=date1, end=None,
			host=user['_id'], invitees=[], pictureDir='events.jpg', private=True).json()
	# event_id = event_obj.insert(user['email'])
	# event = DB.find_one(collection="Events", query={"_id": ObjectId(event_id)})
	# if event is None:
	# 	flash('Please contact admin, event doesn\'t exist!')
	# 	return redirect(url_for('polls'))
	form = EventForm()
	if form.validate_on_submit():
		form.starttime.data = form.starttime.data.split(' ')
		time1 = form.starttime.data[0].split(':')
		if form.starttime.data[1] == 'PM': 
			time1[0] = int(time1[0]) + 12
			if time1[0] == 24:
				time1[0] = 0
		time1 = time(int(time1[0]), int(time1[1]))

		form.endtime.data = form.endtime.data.split(' ')
		time2 = form.endtime.data[0].split(':')
		if form.endtime.data[1] == 'PM': 
			time2[0] = int(time2[0]) + 12
			if time2[0] == 24:
				time2[0] = 0
		time2 = time(int(time2[0]), int(time2[1]))

		date1 = datetime((form.start.data).year,(form.start.data).month,(form.start.data).day, time1.hour, time1.minute)
		date2 = datetime((form.end.data).year,(form.end.data).month,(form.end.data).day, time2.hour, time2.minute)
		# check date and time
		if date1 < datetime.now():
			flash('Start has to be today or later!')
			return render_template('poll-create-event.html', title = "Create Your Event", form = form, event=event)
		elif date2 < date1:
			flash('End cannot be earlier than Start!')
			return render_template('poll-create-event.html', title = "Create Your Event", form = form, event=event)
		elif date1 == date2:
			flash('Start and End cannot be the same!')
			return render_template('poll-create-event.html', title = "Create Your Event", form = form, event=event)
		if form.pictureDir.data is None:
			filename = "event.jpg"
		else:
			filename = photos.save(form.pictureDir.data, name= 'event/' + str(user['_id']) + '.')
			filename = filename.split('/')[1]

		form.name.data = form.name.data.strip()
		form.description.data = form.description.data.strip()
		if form.eventType.data == 'private':
			event_type = True
		else:
			event_type = False

		#TODO invitees

		# for profile in event['invitees']:
		# 	DB.update_one(collection = "Profile", filter = {"email":profile}, data = {"$pull": {"events" : event['_id']}})
		# DB.remove(collection = "Events", condition = {"_id": event['_id']})
		updated_event = Event(name = form.name.data, description = form.description.data,
						  start = date1, end =date2,
						  host=user['_id'],
						  invitees=[], pictureDir=filename, private=event_type)
		updated_event.insert(user['email'])
		# DB.replace_one(collection="Events", filter={"_id": ObjectId(event_id)}, data=updated_event)
		return redirect(url_for('delete_poll', poll=poll))
	return render_template('poll-create-event.html', title = "Create Your Event", form=form, poll=poll, event=event_obj)

@app.route('/add-people/<email>/<id>')
@login_required
def addPeople(email = None,id = None):
	#Add People To the first ( only friends i guess)
	# need to get the users friends lel

	return redirect(url_for("display_event", id = id))
