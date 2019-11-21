from app import app
from app.database import DB
from app.models.poll import Poll, Option
from app.controllers.forms import PollForm
from app.utility.utility import get_index_1key
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from datetime import datetime, time
from bson.objectid import ObjectId
import ast

def polls_in_profile(pollList):
	polls = []
	for poll in pollList:
		toAdd = DB.find_one(collection='Poll', query={'_id': poll})
		polls.append(toAdd)
	return polls

@app.route('/create-poll', methods=['GET', 'POST'])
@login_required
def create_poll():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	form = PollForm()
	if form.validate_on_submit():
		form.option1t.data = form.option1t.data.split(' ')
		time1 = form.option1t.data[0].split(':')
		if form.option1t.data[1] == 'PM': 
			time1[0] = int(time1[0]) + 12
		time1 = time(int(time1[0]), int(time1[1]))

		form.option2t.data = form.option2t.data.split(' ')
		time2 = form.option2t.data[0].split(':')
		if form.option2t.data[1] == 'PM': 
			time2[0] = int(time2[0]) + 12
		time2 = time(int(time2[0]), int(time2[1]))

		form.option3t.data = form.option3t.data.split(' ')
		time3 = form.option3t.data[0].split(':')
		if form.option3t.data[1] == 'PM': 
			time3[0] = int(time3[0]) + 12
		time3 = time(int(time3[0]), int(time3[1]))
		option1 = datetime((form.option1.data).year, (form.option1.data).month, (form.option1.data).day, time1.hour, time1.minute)
		option2 = datetime((form.option2.data).year, (form.option2.data).month, (form.option2.data).day, time2.hour, time2.minute)
		option3 = datetime((form.option3.data).year, (form.option3.data).month, (form.option3.data).day, time3.hour, time3.minute)
		form.name.data = form.name.data.strip()
		form.description.data = form.description.data.strip()
		# option_obj1 = Option(option1, [])
		# option_obj2 = Option(option2, [])
		# option_obj3 = Option(option3, [])
		# print(option1)
		# print(option2)
		# print(option3)
		poll_obj = Poll(creator=ObjectId(user['_id']), name=form.name.data, description=form.description.data, options=[{'date':option1}, {'date':option2}, {'date':option3}], voters=[])
		poll_id = poll_obj.insert()
		# DB.update_one(collection='Poll', filter={'_id': poll_id}, data={'$push': {'options': [{'date':option1}, {'date':option2}, {'date':option3}]}})
		# DB.update_one(collection = "Profile", filter = {"email": current_user.email}, data={"$push": {"polls": ObjectId(poll_id)}})
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
	DB.update_one(collection="Profile", filter={'_id': ObjectId(friend['_id'])}, data={'$push':{'polls': ObjectId(poll)}})
	flash(f'Successfully added {email} as voter!')
	return redirect(url_for('add_voter', poll=poll))

@app.route('/polls')
@login_required
def polls():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	pollList = polls_in_profile(user['polls'])
	return render_template('poll.html',title="View Polls", polls=pollList, user=user)

@app.route('/update-vote/<poll>', methods=['GET', 'POST'])
@login_required
def update_vote(poll):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	toUpdate = DB.find_one(collection='Poll', query={'_id': ObjectId(poll)})
	if toUpdate is None:
		flash('Please contact admin, DB error!')
		return redirect(url_for('polls'))
	options = request.form.getlist('date')
	# print(options)
	# counter = 0 
	if request.form.get('add') == 'add':
		for dates in options:
			# dates = dates.split(' ')[0]
			dt = datetime.strptime(dates, "%Y-%m-%d %H:%M:%S")
			print(f'LOL {dates}')
			# test = DB.find_one(collection='Poll', query={'options': dt})
			# print(test)
			index = get_index_1key(arrayList=toUpdate, key='options', query=dt)
			print(index)
			index = "options." + str(index) + ".voters"
			check = DB.find_one(collection='Poll', query={index: user['firstName']})
			if check is not None:
				flash(f'You Already voted for {dt}')
				continue
			DB.update_one(collection='Poll', filter={'_id': ObjectId(poll)}, data={'$push': {index: user['firstName']}})
			return redirect(url_for('polls'))
	elif request.form.get('del') == 'del':
		for dates in options:
			# dates = dates.split(' ')[0]
			dt = datetime.strptime(dates, "%Y-%m-%d %H:%M:%S")
			# print(dt)
			# test = DB.find_one(collection='Poll', query={'options': dt})
			# print(test)
			index = get_index_1key(arrayList=toUpdate, key='options', query=dt)
			print(index)
			index = "options." + str(index) + ".voters"
			check = DB.find_one(collection='Poll', query={index: user['firstName']})
			if check is None:
				flash(f'You haven\'t voted for {dt}')
				continue
			DB.update_one(collection='Poll', filter={'_id': ObjectId(poll)}, data={'$pull': {index: user['firstName']}})
			return redirect(url_for('polls'))
	flash(f'Pick an option')	
	return redirect(url_for('polls'))
		
