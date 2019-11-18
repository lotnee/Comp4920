from app import app
from app.database import DB
from app.models.events import Event
from app.models.friend import Friend
from app.controllers.forms import photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.utility import get_list, get_cursor
from datetime import datetime
from bson.objectid import ObjectId

def profileEvents(eventLists):
	retList = []
	for item in eventLists:
		event = DB.find_one(collection="Events",query={'_id':item})
		retList.append(event)
	return retList

@app.route('/newevent', methods=['GET', 'POST'])
@login_required
def events():
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
					  start = date1, end =date2, admin = current_user.email,
				      profileList=[current_user.email])
		# print(event)
		event.insert(current_user.email)

		return redirect(url_for('eventCompleted'))
	return render_template('newevent.html', title = "Create Your Event", form = form)

@app.route('/viewevents')
@login_required
def viewEvents():
   if DB.find_one(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}}):
      eventList = DB.find(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}})
      allEvents = profileEvents(eventList[0]['events'])
      return render_template('events.html', events = allEvents, title='View Events')
   return render_template('events.html',title="View Events")

@app.route('/eventcompleted')
@login_required
def eventCompleted():
	return render_template('eventCompleted.html',title="Event Creation Completed")

@app.route('/viewevents/<path:name>')
@login_required
def displayevent(name):
	#get the event name or more so the ID
	return render_template('displayevent.html', title=name)

@app.route('/deleteEvent/<string:id>')
@login_required
def deleteEvent(id):
	#delete the event from the id
	#first go through all the users that is associated with that id
	x = DB.find_one(collection="Events", query = {"_id":ObjectId(id)})
	profileList = x['profileList']
	# Delete the event from all users in profile
	for profile in profileList:
		DB.update_one(collection = "Profile", filter = {"email":profile}, data = {"$pull": {"events" : ObjectId(id)}})
	#delete the actual event from the database
	DB.remove(collection = "Events", condition = {"_id": ObjectId(id)})
	return "hi"
