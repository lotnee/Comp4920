from app import app
from app.database import DB
from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

	# This searches the database profile information for a match in the
	# first name or last name. It relies on the Profile collection having a
	# text index set on it in the database, I used the pymongo command:
	# `db.Profile.create_index([('firstName', TEXT), ('lastName', TEXT)],
	# name='profile_search')` to create it.

	matched_profiles = DB.find(collection='Profile',query={
			'$text': {'$search': request.args['query']}
		})

	return render_template('search.html', title='Search Results',
			matched_profiles=matched_profiles)

