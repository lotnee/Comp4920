from app import app
from app.database import DB
from .forms import LoginForm
from app.models.user import User
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, login_required
from werkzeug.security import check_password_hash

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html')

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = DB.find_one("User",{"email": form.email.data})
		if user and check_password_hash(user['password'], form.password.data):
			user_obj = User(email=user['email'], password=user['password'], name=user['name'])
			# print(user_obj.email)
			login_user(user_obj)
			# flash(user_obj.name)
			return redirect(url_for('dashboard'))
			# next_page = request.args.get('next')
			# if not next_page or url_parse(next_page).netloc != '':
			#     next_page = url_for('index')
			# return redirect(next_page)
		else:
			flash("Invalid username or password")
	return render_template('login.html', title='Log In', form=form)
