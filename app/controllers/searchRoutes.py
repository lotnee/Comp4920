from app import app
from app.database import DB
from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required
from bson.objectid import ObjectId
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
	user = DB.find_one(collection="Profile", query={"email": current_user.email})
	if user is None:
		flash('Please create your profile first!')
		return redirect(url_for('edit_profile'))

	# create index for text search (Profile)
	DB.createIndex(collection="Profile", query=[("email", "text"), ("firstName", "text"), ("lastName", "text"), ("descriptions", "text")], name='profile_search')
	matched_profiles = list(DB.find(collection='Profile',query={
			'$text': {'$search': request.args['query']}
		}))
	print("The matched profile is ",matched_profiles)

	# since the host of an event can change, or the name of the host can
	# change, we need to look up event hosts by profile id instead of by
	# name
	matched_profile_info = {profile['_id'] : (profile['firstName'], profile['lastName'])
				for profile in matched_profiles}

	print("\n",matched_profile_info)

	DB.createIndex(collection="Events", query=[("name", "text"), ("description", "text")], name='event_search')
	DB.createIndex(collection="Events", query=[("host", 1)], name='event_host')
	matched_events = list(DB.find(collection='Events', query= {
		'$or':[{'$text': {'$search': request.args['query']}},
			{'host': {'$in': list(matched_profile_info.keys())}}]
		}))
	print("====================================================")
	for event in matched_events:
		matched_user = DB.find_one(collection = "Profile", query = {"_id": event['host']}, projection = {"firstName":1, "lastName":1} )
		(firstname, lastname) = (matched_user['firstName'], matched_user['lastName'])
		event['host'] = '{} {}'.format(firstname,lastname)
	print("====================================================")
	#matched_events = [item for item in matched_events if item['private'] == False]
	return render_template('search.html', title='Search Results',
		users=matched_profiles, events=matched_events, query=request.args['query'])
