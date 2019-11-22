from app import app
from app.database import DB
from app.utility.utility import get_list, get_cursor, get_index_2key
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from bson.objectid import ObjectId

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	users = list(DB.find_all(collection="Profile"))
	me = DB.find_one(collection="Profile", query={"email": current_user.email})

	myFriendList = []
	mySentList = []
	for f in me['friends']:
		profile = DB.find_one(collection="Profile", query={'_id': f['friend_id']})
		if f['status'] == 'accepted':
			myFriendList.append(profile)
		else:
			mySentList.append(profile)
	incoming = DB.find(collection="Profile", query={"friends": {"$elemMatch": {"friend_id": user['_id'], "status": "pending"}}})
	requests = get_cursor(cursor_obj=incoming, key="friends", subkey="friend_id", subkey2="status", query=user['_id'], query2="pending")

	return render_template('friend.html', title='Friend List', users=users, myFriendList=myFriendList, mySentList=mySentList, requests=requests)

@app.route('/send-request/<profile_id>')
@login_required
def send_request(profile_id):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"_id": ObjectId(profile_id)})
	if friend is None:
		flash('User not found!')
		return redirect(url_for('friends'))
	for f in user['friends']:
		if friend['_id'] == f['friend_id'] and f['status'] == 'accepted':
			flash('%s has already accepted your friend request!' % friend['email'])
			return redirect(url_for('friends'))
		elif friend['_id'] == f['friend_id'] and f['status'] == 'pending':
			flash('Already sent %s a friend request!' % friend['email'])
			return redirect(url_for('friends'))
	for f in friend['friends']:
		if user["_id"] == f['friend_id']:
			flash('%s already sent you a friend request!' % friend['email'])
			return redirect(url_for('friends'))
	DB.update_one(collection="Profile", filter={"_id": user['_id']}, data={"$push": {"friends": {"friend_id": friend['_id'], "status": "pending"}}})

	flash('Friend request sent to ' + friend['email'] + '!')
	return redirect(url_for('friends'))

@app.route('/delete-request/<profile_id>')
@login_required
def delete_request(profile_id):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"_id": ObjectId(profile_id)})
	if friend is None:
		flash('User not found!')
		return redirect(url_for('friends'))
	for f in user['friends']:
		if friend['_id'] == f['friend_id'] and f['status'] == 'pending':
			DB.update_one(collection="Profile", filter={"_id": user['_id']}, data={'$pull': {"friends":f}})
			flash('Friend request ' + friend['email'] + ' cancelled!')
			return redirect(url_for('friends'))
	for f in friend['friends']:
		if user['_id'] == f['friend_id'] and f['status'] == 'pending':
			DB.update_one(collection="Profile", filter={"_id": friend['_id']}, data={'$pull': {"friends":f}})
			flash('Friend request ' + friend['email'] + ' rejected!')
			return redirect(url_for('friends'))
	flash('Please contact admin, DB issues!')
	return redirect(url_for('friends'))
	
@app.route('/accept-request/<profile_id>')
@login_required
def accept_request(profile_id):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"_id": ObjectId(profile_id)})
	if friend is None:
		flash('User not found!')
		return redirect(url_for('friends'))
	if friend['friends'] != []:
		index = get_index_2key(arrayList=friend['friends'], key='friend_id', query=user['_id'], key2='status', query2='pending')
		if index == -1:
			flash('invalid request')
			return redirect(url_for('friends'))
		else:
			friend_status = "friends." + str(index) + ".status"
			DB.update_one(collection="Profile", filter={"_id": friend['_id']}, data={"$set": {friend_status: "accepted"}})
			DB.update_one(collection="Profile", filter={"_id": user['_id']}, data={"$push": {"friends": {"friend_id": friend['_id'], "status": "accepted"}}})
			flash('Accepted %s\'s friend request!' % friend['email'])
			return redirect(url_for('friends'))
	flash('pontential DB issue pls contact admin')
	return redirect(url_for('friends'))

@app.route('/delete-friend/<profile_id>')
@login_required
def delete_friend(profile_id):
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))

	added = DB.find_one(collection="Profile", query={"$and": [{"_id": user['_id']}, {"friends": {"$elemMatch": {"friend_id": ObjectId(profile_id), "status": "accepted"}}}]})
	added2 = DB.find_one(collection="Profile", query={"$and": [{"_id": ObjectId(profile_id)}, {"friends": {"$elemMatch": {"friend_id": user['_id'], "status": "accepted"}}}]})
	
	if added is not None and added2 is not None:
		myFriendList = get_list(toFilterList=added['friends'], key="friend_id", query=ObjectId(profile_id))
		DB.update_one(collection="Profile", filter={"_id": user['_id']}, data={'$pull': {"friends":myFriendList[0]}})
		theirFriendList = get_list(toFilterList=added2['friends'], key="friend_id", query=user['_id'])
		DB.update_one(collection="Profile", filter={"_id": ObjectId(profile_id)}, data={'$pull': {"friends": theirFriendList[0]}})
		flash(f'Delete friend successful!')
		return redirect(url_for('friends'))
	else:
		flash(f'Delete friend failed!')
		flash('pontential DB issue pls contact admin')
	return redirect(url_for('friends'))
