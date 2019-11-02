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

@app.route('/events', methods=['GET', 'POST'])
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
		return render_template('eventCompleted.html', title="Event Creation Completed")
	return render_template('events.html', title = "Create Your Event", form = form)
