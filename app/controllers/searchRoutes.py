from app import app
from app.database import DB
from flask import render_template, redirect, request, url_for
from flask_login import current_user, login_required

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

	me = DB.find_one(collection='Profile', query={
		'email': current_user.email})

	matched_profiles = DB.find(collection='Profile',query={
			'$text': {'$search': request.args['query']}
		})

	return render_template('search.html', title='Search Results',
		users=matched_profiles,query=request.args['query'])

