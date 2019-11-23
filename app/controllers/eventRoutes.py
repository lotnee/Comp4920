from app import app
from app.database import DB
from app.models.events import Event
from app.controllers.forms import photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.utility.utility import get_list, get_cursor,get_name
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
		event.insert(current_user.email, me['_id'])
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
		return render_template('events.html', events = allEvents, title='View Events', me=user)
	return render_template('events.html',title="View Events")

@app.route('/event-completed')
@login_required
def event_completed():
	return render_template('event-completed.html',title="Event Creation Completed")

@app.route('/view-events/<path:id>')
@login_required
def display_event(id):
	#get the event name or more so the ID
	invited = []
	going = []
	maybe = []
	declined = []
	status = "invited" # this user has not  responded to the event
	host = 0 # whether this person is the host of the event being displayed
	cohosts = []
	invitePrivleges = 0
	eventDetails = DB.find_one(collection = "Events", query = {"_id":ObjectId(id)})
	# gets all the friends of the user
	retDictionary = DB.find_one(collection = "Profile", query = {"email":current_user.email})
	friends = []
	for person in retDictionary['friends']:
		if person['status'] == "accepted":
			friendId = str(person['friend_id'])
			friendDetails = DB.find_one(collection = "Profile", query ={"_id":person['friend_id']})
			element = {"id":friendId, "firstName":friendDetails['firstName'], "lastName": friendDetails['lastName']}
			friends.append(element)
	# Sees whether this person has invite privleges or is a host
	if eventDetails['host'] == retDictionary['_id']:
		host = 1
	else:
		for cohost in eventDetails['invitePrivleges']:
			if(cohost['email'] == current_user.email):
				invitePrivleges = 1
				break
	cohosts = eventDetails['invitePrivleges']
	# see whether the person has accepted or not to give them the option to accept your invite
	for invitee in eventDetails["invitees"]:
		details = DB.find_one(collection = "Profile", query = {"email":invitee['email']},
		 						projection = {"firstName": 1, "lastName" : 1, "pictureDir":1})
		#get pictureDir
		fullName = details['firstName'] + " " +details['lastName']
		pictureDir = details['pictureDir']
		dictionaryItem = {"name":fullName, "pictureDir": pictureDir}
		if invitee['status'] == "going":
			going.append(dictionaryItem)
		elif invitee['status'] == "declined":
			declined.append(dictionaryItem)
		elif invitee['status'] == "maybe":
			maybe.append(dictionaryItem)
		else:
			invited.append(dictionaryItem)
		if invitee["email"] == current_user.email and invitee['status'] != "invited":
			status = invitee['status'] # user has already responded

	return render_template('display-event.html', event = eventDetails,
							friends = json.dumps(friends), host = host, status = status,
							invited = invited,maybe = maybe, going = going,
							declined = declined, canInvite = invitePrivleges,
							cohosts = cohosts)

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
	profileList = x['invitees']
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

	date1 = None
	largest = 0
	for option in my_poll['options']:
		if 'voters' in option:
			if len(list(option['voters'])) > largest:
				largest = len(list(option['voters']))
				date1 = option['date']

	event_obj = Event(name=my_poll['name'] , description =
			my_poll['description'], start=date1, end=None,
			host=user['_id'], invitees=[], pictureDir='events.jpg', private=True).json()

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
			return render_template('poll-create-event.html', title="Create Your Event", form=form, poll=poll, event=event_obj)
		elif date2 < date1:
			flash('End cannot be earlier than Start!')
			return render_template('poll-create-event.html', title="Create Your Event", form=form, poll=poll, event=event_obj)
		elif date1 == date2:
			flash('Start and End cannot be the same!')
			return render_template('poll-create-event.html', title="Create Your Event", form=form, poll=poll, event=event_obj)
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

		inviteesList = []
		for voter in my_poll['voters']:
			voter_obj = DB.find_one(collection='Profile', query={'_id': voter})
			voter_dict = {'email': voter_obj['email'], 'status': 'going'}
			inviteesList.append(voter_dict)

		updated_event = Event(name = form.name.data, description = form.description.data,
						  start = date1, end =date2,
						  host=user['_id'],
						  invitees=inviteesList, pictureDir=filename, private=event_type)
		eventid = updated_event.insert(user['email'], user['_id'])

		for invitees in inviteesList:
			DB.update_one(collection = "Profile", filter = {"email":invitees['email']}, data = {"$push": {"events": ObjectId(eventid)}})

		return redirect(url_for('delete_poll', poll=poll))
	return render_template('poll-create-event.html', title = "Create Your Event", form=form, poll=poll, event=event_obj)

@app.route('/add-people/<userId>/<id>')
@login_required
def addPeople(userId = None,id = None):
	# we have the email and id of the user & event we want to invite,
	# we need to update the number of people in the invitees (add the profile to it)
	# also update the profile's thingy
	profileEvents = DB.find_one(collection = "Profile", query ={"_id" : ObjectId(userId) })
	email = profileEvents['email']
	profileEvents = profileEvents['events']
	if ObjectId(id) not in profileEvents:
		DB.update_one(collection = "Events", filter ={'_id':ObjectId(id)}, data = {'$push': {"invitees": {"id":ObjectId(userId),"email": email, "status": "invited"}}})
		DB.update_one(collection = "Profile", filter = {"email":email}, data = {"$push": {"events": ObjectId(id)}})
	return redirect(url_for("display_event", id = id))


@app.route('/accept-invite/<eventId>/<acceptance>')
@login_required
def acceptInvite(eventId, acceptance):
	#need to change the user to accepting that event id
	DB.update_one(collection = "Events", filter = {"_id":ObjectId(eventId), "invitees":{"$elemMatch": {"email" : current_user.email} } }, data = {'$set': {"invitees.$.status":acceptance}}  )

	return  redirect(url_for("display_event", id = eventId))

@app.route('/delete-invite/<eventId>/<userId>')
@login_required
def deleteInvite(eventId,userId):
	# Delete user from the Event model from invitees
	# Get the list of invitees from Event model
	userEmail = DB.find_one(collection = "Profile", query  = {"_id":ObjectId(userId)}, projection = {"email":1})
	DB.update_one(collection = "Events", filter = {"_id": ObjectId(eventId)}, data = { "$pull" : {"invitees": {"id": ObjectId(userId)}}})
	DB.update_one(collection = "Profile", filter = {"_id":ObjectId(userId)}, data = {"$pull": {"events":ObjectId(eventId)}})

	# also remove the person from the invitePrivleges
	return redirect(url_for("display_event", id = eventId))

@app.route('/edit-event/<eventId>', methods=['GET', 'POST'])
@login_required
def edit_event(eventId):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	event = DB.find_one(collection="Events", query={"_id": ObjectId(eventId)})
	if event is None:
		flash('Please contact admin, DB issues!')
		return redirect(url_for('view_events'))
	form = EventForm()
	if form.validate_on_submit():
		if form.pictureDir.data is not None:
			if event['pictureDir'] == 'event.jpg':
				filename = photos.save(form.pictureDir.data, name='event/' + str(event['_id']) + '.')
				filename = filename.split('/')[1]
			else:
				# delete existing photo
				filename = "app/static/images/event/" + profile['pictureDir']
				os.remove(os.path.join(filename))
				filename = photos.save(form.pictureDir.data, name='event/'+ + str(event['_id']) + '.')
				filename = filename.split('/')[1]
			DB.update_one(collection="Events", filter={"_id": event['_id']}, data={"$set": {"pictureDir": filename}})
		if form.eventType.data == 'private':
			event_type = True
		else:
			event_type = False

		DB.update_one(collection="Events", filter={"_id": event['_id']}, data={"$set": {"name": form.name.data.strip()}})
		DB.update_one(collection="Events", filter={"_id": event['_id']}, data={"$set": {"description": form.description.data.strip()}})
		DB.update_one(collection="Events", filter={"_id": event['_id']}, data={"$set": {"private": event_type}})
		return redirect(url_for('view_events'))
	return render_template('edit-event.html', title = "Edit Event Details", form=form, event=event)


# In this case when we write userId it is really the profile Id
@app.route('/add-coHost/<userId>/<eventId>')
@login_required
def add_cohost(userId, eventId):
	# Add the userId to the event invitePrivleges
	person = DB.find_one(collection = "Events", query = {"_id":ObjectId(eventId), "invitePrivleges": {"$elemMatch": {"cohostId": ObjectId(userId)}}})
	if person is None:
		userDetails = DB.find_one(collection = "Profile", query = {"_id":ObjectId(userId)}, projection = {"email":1, "firstName":1,"lastName":1, "pictureDir": 1})
		DB.update_one(collection = "Events", filter = {"_id":ObjectId(eventId)}, data =
														{"$push": {"invitePrivleges":
														{"email":userDetails['email'],
														"cohostId":ObjectId(userId),
														"pictureDir":userDetails['pictureDir'],
														"name": userDetails['firstName'] + " " + userDetails['lastName']
														}}})
	return redirect(url_for('display_event', id = eventId))


@app.route('/delete-coHost/<userId>/<eventId>')
@login_required
def delete_cohost(userId, eventId):
	# Add the userId to the event invitePrivleges

	DB.update_one(collection = "Events", filter = {"_id":ObjectId(eventId)}, data = {"$pull": {"invitePrivleges": ObjectId(userId)}})
	return redirect(url_for('display_event', id = eventId))
