from app import app
from app.database import DB
from app.utility import get_list, get_cursor
from app.models.profile import Profile
from app.models.events import Event
from app.models.friend import Friend
from app.controllers.forms import photos,EventForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime

def profileEvents(eventLists):
	retList = []
	for item in eventLists:
		event = DB.find_one(collection="Events",query={'_id':item})
		retList.append(event)
	print(retList[0]['name'])
	return retList

@app.route('/newevent', methods=['GET', 'POST'])
@login_required
def events():
	form = EventForm()
	if form.is_submitted():
		print(type(form.start.data))
		date1 = datetime((form.start.data).year,(form.start.data).month,(form.start.data).day)
		date2 = datetime((form.end.data).year,(form.end.data).month,(form.end.data).day)
		print("start date is " + date1.isoformat())
		print("end date is" + date2.isoformat())
		event = Event(name = form.name.data, description = form.description.data, start = date1, end = date2)
		event.insert(current_user.email)
		return redirect(url_for('eventCompleted'))
	return render_template('newevent.html', title = "Create Your Event", form = form)

@app.route('/viewevents')
@login_required
def viewEvents():
   if DB.find_one(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}}):
      eventList = DB.find(collection="Profile", query={"email":current_user.email, "events": {"$ne" : []}})
      print(eventList[0]['events'])
      allEvents = profileEvents(eventList[0]['events'])
      return render_template('events.html', events = allEvents, title='View Events')
   return render_template('events.html',title="View Events")

@app.route('/eventcompleted')
@login_required
def eventCompleted():
	return render_template('eventCompleted.html',title="Event Creation Completed")

@app.route('/viewevents/<name>')
@login_required
def displayevent(name):
	return render_template('displayevent.html', title=name)
