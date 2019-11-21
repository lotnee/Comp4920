from app import app
from app.database import DB
from app.models.events import Event
from app.models.friend import Friend
from app.controllers.forms import photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.utility.utility import get_list, get_cursor
from datetime import datetime
from bson.objectid import ObjectId

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
		print(type(form.start.data))
		date1 = datetime((form.start.data).year,(form.start.data).month,(form.start.data).day)
		date2 = datetime((form.end.data).year,(form.end.data).month,(form.end.data).day)
		# print("start date is " + date1.isoformat())
		# print("end date is " + date2.isoformat())
		# print(f'Name : {form.name.data}')
		# print(f'Description :{form.description.data}')
		# print(f'Cover Photo :{form.pictureDir.data}')
		event = Event(name = form.name.data, description = form.description.data,
					  start = date1, end =date2, host = '{} {}'.format(user['firstName'], user['lastName']),
					  invitees=[current_user.email])
		# print(event)
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
		return render_template('events.html', events = allEvents, title='View Events')
	return render_template('events.html',title="View Events")

@app.route('/event-completed')
@login_required
def event_completed():
	return render_template('event-completed.html',title="Event Creation Completed")

@app.route('/view-events/<path:name>')
@login_required
def display_event(name):
	#get the event name or more so the ID
	return render_template('display-event.html', title=name)

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
		DB.update_one(collection = "Profile", filter = {"email":profile}, data = {"$pull": {"events" : ObjectId(id)}})
	#delete the actual event from the database
	DB.remove(collection = "Events", condition = {"_id": ObjectId(id)})
	return "hi"
