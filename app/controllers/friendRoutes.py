from app import app
from app.database import DB
from app.utility import get_list, get_cursor, get_index
from app.models.profile import Profile
from app.models.friend import Friend
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
	users = list(DB.find_all(collection="Profile"))
	me = DB.find_one(collection="Profile", query={"email": current_user.email}) 
	incoming = DB.find(collection="Profile", query={"friends": {"$elemMatch": {"email": current_user.email, "status": "pending"}}})
	# print(incoming.count())
	# print(incoming[0]['email'])
	# print(incoming[0]['friends'])
	requests = get_cursor(cursor_obj=incoming, key="friends", subkey="email", subkey2="status", query=current_user.email, query2="pending")
	# print(len(requests))
	# print(requests[0])
	# print(requests[1])
	return render_template('friend.html', title='Friend List', users=users, me=me, requests=requests)

@app.route('/send-request/<email>')
@login_required
def send_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "accepted"}}}]})
	# sent = get_list(added['friends'], "status", "pending")
	sent = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "pending"}}}]})
	if added is not None:
		flash('%s has already accepted your friend request!' % email)
		return redirect(url_for('friends'))
	if sent is not None:
		flash('Request to %s sent!' % email)
		return redirect(url_for('friends'))
	friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="pending", pictureDir=friend['pictureDir'])
	friend_obj.insert(current_user.email)
	flash('Friend request sent to ' + email + '!')
	return redirect(url_for('friends'))

@app.route('/delete-request/<email>')
@login_required
def delete_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	# friend = DB.find(collection="Profile", query={"email": email})
	# print(friend[0])
	# friendList = get_list(friend, 'friends')
	# size of the cursor objects
	# print(friend.count())
	# size of the array in object
	# print(len(friend[0]['friends']))

	# the functions below can be used for invitees
	added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email}}}]})
	added2 = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email}}}]})

	if added and added2 is not None:
		myFriendList = get_list(added['friends'], "email", email)
		theirFriendList = get_list(added2['friends'], "email", current_user.email)

		friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
		friend_obj.remove(current_user.email)
		friend_obj2 = Friend(email=theirFriendList[0]['email'], firstName=theirFriendList[0]['firstName'], lastName=theirFriendList[0]['lastName'], status=theirFriendList[0]['status'], pictureDir=theirFriendList[0]['pictureDir'])
		friend_obj2.remove(email)
		flash('Friend request ' + email + ' deleted!')
	elif added is not None:
		myFriendList = get_list(added['friends'], "email", email)
		# print(myFriendList)
		# print(myFriendList[0]['email'])
		friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
		friend_obj.remove(current_user.email)
		flash('Friend request ' + email + ' cancelled!')
	elif added2 is not None:
		theirFriendList = get_list(added2['friends'], "email", current_user.email)
		# print(theirFriendList)
		friend_obj = Friend(email=theirFriendList[0]['email'], firstName=theirFriendList[0]['firstName'], lastName=theirFriendList[0]['lastName'], status=theirFriendList[0]['status'], pictureDir=theirFriendList[0]['pictureDir'])
		friend_obj.remove(email)
		flash('Friend request ' + email + ' rejected!')
	return redirect(url_for('friends'))

@app.route('/accept-request/<email>')
@login_required
def accept_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"friends.email": current_user.email, "friends.status": "pending"})
	# print(added['email'])
	# print(added['friends'])
	if added is not None:
		index = get_index(arrayList=friend['friends'], key="email", query=current_user.email, key2="status", query2="pending")
		# print(index)
		if index != -1:
			friend_status = "friends." + str(index) + ".status"
			DB.update_one(collection="Profile", filter={"friends.email": current_user.email}, data={"$set": {friend_status: "accepted"}})
			friend_obj = Friend(email=friend['email'], firstName=friend['firstName'], lastName=friend['lastName'], status="accepted", pictureDir=friend['pictureDir'])
			friend_obj.insert(current_user.email)
			flash('Accepted %s\'s friend request!' % email)
		else:
			flash('invalid request')
		return redirect(url_for('friends'))
	flash('%s is already a friend' % email)
	return redirect(url_for('friends'))
