from app import app
from app.database import DB
from app.models.poll import Poll
from app.controllers.forms import PollForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from datetime import datetime
from bson.objectid import ObjectId

@app.route('/create-poll', methods=['GET', 'POST'])
@login_required
def create_poll():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	form = PollForm()
	if form.validate_on_submit():
		option1 = datetime((form.option1.data).year, (form.option1.data).month, (form.option1.data).day)
		option2 = datetime((form.option2.data).year, (form.option2.data).month, (form.option2.data).day)
		option3 = datetime((form.option3.data).year, (form.option3.data).month, (form.option3.data).day)
		form.name.data = form.name.data.strip()
		form.description.data = form.description.data.strip()
		poll_obj = Poll(creator=ObjectId(user['_id']), name=form.name.data, description=form.description.data, options=[option1, option2, option3], voters=[])
		poll_id = poll_obj.insert()
		DB.update_one(collection = "Profile", filter = {"email": current_user.email}, data={"$push": {"polls": ObjectId(poll_id)}})
		return redirect(url_for('add_voter', poll=poll_id))
	return render_template('create-poll.html', title = 'create a poll', form=form)

@app.route('/add-voter/<poll>', methods=['GET', 'POST'])
@login_required
def add_voter(poll):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	# check poll need at least 1-2 voter
	current_poll = DB.find_one(collection="Poll", query={"_id": ObjectId(poll)})
	if current_poll is None:
		flash('Please contact admin, DB error!')
		return redirect(url_for('create_poll'))
	return render_template('add-voter.html', title = 'Add voter', me=user, poll=poll)

@app.route('/invite-voter/<poll>/<email>')
@login_required
def invite_voter(poll, email):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash(f'Friend {email} not found!')
		return redirect(url_for('add_voter', poll=poll))
	sent = DB.find_one(collection="Poll", query={'$and': [{'_id': ObjectId(poll)}, {'voters': ObjectId(friend['_id'])}]})
	if sent is not None:
		flash(f'Already added {email} as voter!')
		return redirect(url_for('add_voter', poll=poll))
	DB.update_one(collection="Poll", filter={'_id': ObjectId(poll)}, data={'$push':{'voters': ObjectId(friend['_id'])}})
	flash(f'Successfully added {email} as voter!')
	return redirect(url_for('add_voter', poll=poll))

@app.route('/polls')
@login_required
def polls():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	pollList = DB.find_one(collection='Profile', query={'email': current_user.email, 'polls': {'$ne': []}})
	if pollList is None:
		return render_template('poll.html',title="View Polls")
	return render_template('poll.html',title="View Polls", polls=pollList['polls'])

@app.route('/update-poll/<poll>')
@login_required
def update_poll(poll):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	toUpdate = DB.find_one(collection='Poll', query={'_id': ObjectId(poll)})
	if toUpdate is None:
		flash('Please contact admin, DB error!')
		return redirect(url_for('polls'))
	if request.form.getlist('date1'):
		print(type(request.form.getlist('date1')))
	if request.form.getlist('date2'):
		print(type(request.form.getlist('date2')))
	if request.form.getlist('date3'):
		print(type(request.form.getlist('date3')))
	return redirect(url_for('polls'))

