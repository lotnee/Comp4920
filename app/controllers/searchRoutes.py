from app import app
from app.database import DB
from app.utility.utility import validate_profile
from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
	user = validate_profile(current_user.email)

	# create index for text search (Profile)
	DB.createIndex(collection="Profile", query=[("email", "text"), ("firstName", "text"), ("lastName", "text"), ("descriptions", "text")], name='profile_search')
	matched_profiles = list(DB.find(collection='Profile',query={
			'$text': {'$search': request.args['query']}
		}))

	# since the host of an event can change, or the name of the host can
	# change, we need to look up event hosts by profile id instead of by
	# name
	matched_profile_info = {profile['_id'] : (profile['firstName'], profile['lastName'])
				for profile in matched_profiles}

	DB.createIndex(collection="Events", query=[("name", "text"), ("description", "text")], name='event_search')
	DB.createIndex(collection="Events", query=[("host", 1)], name='event_host')
	matched_events = list(DB.find(collection='Events', query= {
		'$or':[{'$text': {'$search': request.args['query']}},
			{'host': {'$in': list(matched_profile_info.keys())}}]
		}))

	for event in matched_events:
		(firstname, lastname) = matched_profile_info[event['host']]
		event['host'] = '{} {}'.format(firstname,lastname)

	return render_template('search.html', title='Search Results',
		users=matched_profiles, events=matched_events, query=request.args['query'])
