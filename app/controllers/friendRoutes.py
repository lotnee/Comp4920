from app import app
from app.database import DB
from app.utility.utility import get_list, get_cursor, get_index_2key
from app.models.friend import Friend
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

	# friend = DB.find_one(collection="Profile", query={"email": email})
	# if friend is None:
	# 	flash('User %s not found!' % email)
	# 	return redirect(url_for('friends'))
	# # very similar to sending request to invitees
	# added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "accepted"}}}]})
	# sent = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "pending"}}}]})
	# received = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email, "status": "pending"}}}]})
	# # check if is already friend
	# if added is not None:
		# flash('%s has already accepted your friend request!' % email)
		# return redirect(url_for('friends'))
	# # check if alredy sent
	# if sent is not None:
	# 	flash('Request to %s sent!' % email)
	# 	return redirect(url_for('friends'))
	# # check if alredy received friend request
	# if received is not None:
		# flash('%s already sent you a friend request!' % email)
		# return redirect(url_for('friends'))
	# friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="pending", pictureDir=friend['pictureDir'])
	# friend_obj.insert(current_user.email)
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
	# friend = DB.find_one(collection="Profile", query={"email": email})
	# if friend is None:
	# 	flash('User %s not found!' % email)
	# 	return redirect(url_for('friends'))

	# the functions below can be used for invitees
	# sent = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "pending"}}}]})
	# received = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email, "status": "pending"}}}]})

	# if sent is not None:
	# 	myFriendList = get_list(sent['friends'], "email", email)
	# 	friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
	# 	friend_obj.remove(current_user.email)
	# 	flash('Friend request ' + email + ' cancelled!')
	# elif received is not None:
	# 	theirFriendList = get_list(received['friends'], "email", current_user.email)
	# 	friend_obj = Friend(email=theirFriendList[0]['email'], firstName=theirFriendList[0]['firstName'], lastName=theirFriendList[0]['lastName'], status=theirFriendList[0]['status'], pictureDir=theirFriendList[0]['pictureDir'])
	# 	friend_obj.remove(email)
	# 	flash('Friend request ' + email + ' rejected!')
	# return redirect(url_for('friends'))

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
	# friend = DB.find_one(collection="Profile", query={"email": email})
	# if friend is None:
	# 	flash('User %s not found or has not created a profile!' % email)
	# 	return redirect(url_for('friends'))
	# added = DB.find_one(collection="Profile", query={"friends.email": current_user.email, "friends.status": "pending"})
	# if added is not None:
	# 	index = get_index_2key(arrayList=friend['friends'], key="email", query=current_user.email, key2="status", query2="pending")
	# 	if index != -1:
	# 		friend_status = "friends." + str(index) + ".status"

	# 		DB.update_one(collection="Profile", filter={"email": friend['email']}, data={"$set": {friend_status: "accepted"}})
	# 		friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="accepted", pictureDir=friend['pictureDir'])
	# 		friend_obj.insert(current_user.email)
	# 		flash('Accepted %s\'s friend request!' % email)
	# 	else:
	# 		flash('invalid request')
	# 	return redirect(url_for('friends'))
	# flash('%s is already a friend' % email)
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
	# added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "accepted"}}}]})
	# added2 = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email, "status": "accepted"}}}]})

	# if added and added2 is not None:
	# 	myFriendList = get_list(added['friends'], "email", email)
	# 	theirFriendList = get_list(added2['friends'], "email", current_user.email)

	# 	friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
	# 	friend_obj.remove(current_user.email)
	# 	friend_obj2 = Friend(email=theirFriendList[0]['email'], firstName=theirFriendList[0]['firstName'], lastName=theirFriendList[0]['lastName'], status=theirFriendList[0]['status'], pictureDir=theirFriendList[0]['pictureDir'])
	# 	friend_obj2.remove(email)
	# 	flash(f'Deleted {email} successful!')
	else:
		flash(f'Delete friend failed!')
		flash('pontential DB issue pls contact admin')
	return redirect(url_for('friends'))
