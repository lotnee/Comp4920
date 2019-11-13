from app import app
from app.database import DB
from app.models.user import User
from app.controllers.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = DB.find_one(collection="User", query={"email": form.email.data})
		if user and check_password_hash(user['password'], form.password.data):
			user_obj = User(email=user['email'], password=user['password'])
			# print(user_obj.email)
			login_user(user_obj)
			# flash(user_obj.name)
			return redirect(url_for('dashboard'))
			# next_page = request.args.get('next')
			# if not next_page or url_parse(next_page).netloc != '':
			#     next_page = url_for('index')
			# return redirect(next_page)
		else:
			flash("Invalid email or password")
	return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		print("I am here")
		user = DB.find_one(collection="User", query={"email": form.email.data})
		if user is None:
			user_obj = User(email=form.email.data, password=generate_password_hash(form.password.data))
			user_obj.insert()
			login_user(user_obj)
			return redirect(url_for('edit_profile'))
		else:
			flash("Invalid email")
	return render_template('registration.html', title='Sign Up', form=form)
