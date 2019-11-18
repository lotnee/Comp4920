from app import app
from app.database import DB
from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

	# me = DB.find_one(collection='Profile', query={
	# 	'email': current_user.email})
	# create index for text search (Profile)
	DB.createIndex(collection="Profile", query=[("email", "text"), ("firstName", "text"), ("lastName", "text"), ("descriptions", "text")], name='profile_search')

	matched_profiles = DB.find(collection='Profile',query={
			'$text': {'$search': request.args['query']}
		})

	DB.createIndex(collection="Events", query=[("name", "text"), ("description", "text"), ("host", "text")], name='event_search')

	matched_events = DB.find(collection='Events', query= {
			'$text': {'$search': request.args['query']}
		})
	# interesting read on cursor object
	# https://stackoverflow.com/questions/55944581/python-flask-jinja2-templating-nested-mongodb-data-cursor-object
	# print(list(matched_profiles)) 
	# print(list(matched_events))
	return render_template('search.html', title='Search Results',
		users=list(matched_profiles), events=list(matched_events), query=request.args['query'])

