from app import app
from app.database import DB
from app.utility import get_list, get_cursor, get_index
from app.models.friend import Friend
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required

@app.route('/friends', methods=['GET', 'POST'])
@login_required
def friends():
	users = list(DB.find_all(collection="Profile"))
	me = DB.find_one(collection="Profile", query={"email": current_user.email}) 
	incoming = DB.find(collection="Profile", query={"friends": {"$elemMatch": {"email": current_user.email, "status": "pending"}}})
	requests = get_cursor(cursor_obj=incoming, key="friends", subkey="email", subkey2="status", query=current_user.email, query2="pending")

	return render_template('friend.html', title='Friend List', users=users, me=me, requests=requests)

@app.route('/send-request/<email>')
@login_required
def send_request(email):
	# only can add user with a profile
	friend = DB.find_one(collection="Profile", query={"email": email})
	if friend is None:
		flash('User %s not found!' % email)
		return redirect(url_for('friends'))
	# very similar to sending request to invitees
	added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "accepted"}}}]})
	sent = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "pending"}}}]})
	# check if is already friend
	if added is not None:
		flash('%s has already accepted your friend request!' % email)
		return redirect(url_for('friends'))
	# check if alredy sent
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

	# the functions below can be used for invitees
	sent = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "pending"}}}]})
	received = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email, "status": "pending"}}}]})

	if sent is not None:
		myFriendList = get_list(sent['friends'], "email", email)
		friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
		friend_obj.remove(current_user.email)
		flash('Friend request ' + email + ' cancelled!')
	elif received is not None:
		theirFriendList = get_list(received['friends'], "email", current_user.email)
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
		flash('User %s not found or has not created a profile!' % email)
		return redirect(url_for('friends'))
	added = DB.find_one(collection="Profile", query={"friends.email": current_user.email, "friends.status": "pending"})
	if added is not None:
		index = get_index(arrayList=friend['friends'], key="email", query=current_user.email, key2="status", query2="pending")
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
	flash('pontential DB issue pls contact admin')
	return redirect(url_for('friends'))

@app.route('/delete-friend/<email>')
@login_required
def delete_friend(email):
	added = DB.find_one(collection="Profile", query={"$and": [{"email": current_user.email}, {"friends": {"$elemMatch": {"email": email, "status": "accepted"}}}]})
	added2 = DB.find_one(collection="Profile", query={"$and": [{"email": email}, {"friends": {"$elemMatch": {"email": current_user.email, "status": "accepted"}}}]})

	if added and added2 is not None:
		myFriendList = get_list(added['friends'], "email", email)
		theirFriendList = get_list(added2['friends'], "email", current_user.email)

		friend_obj = Friend(email=myFriendList[0]['email'], firstName=myFriendList[0]['firstName'], lastName=myFriendList[0]['lastName'], status=myFriendList[0]['status'], pictureDir=myFriendList[0]['pictureDir'])
		friend_obj.remove(current_user.email)
		friend_obj2 = Friend(email=theirFriendList[0]['email'], firstName=theirFriendList[0]['firstName'], lastName=theirFriendList[0]['lastName'], status=theirFriendList[0]['status'], pictureDir=theirFriendList[0]['pictureDir'])
		friend_obj2.remove(email)
		flash(f'Deleted {email} successful!')
	else:
		flash(f'Deleted {email} failed!')
		flash('pontential DB issue pls contact admin')
	return redirect(url_for('friends'))
