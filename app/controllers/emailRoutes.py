from app import app
from app.database import DB
from app.controllers.forms import PasswordForm
from itsdangerous import URLSafeTimedSerializer
from flask import render_template, flash, redirect, url_for
from werkzeug.security import generate_password_hash

@app.route('/confirm-email/<token>')
def confirm_email(token):
	try:
		serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		email = serializer.loads(token, salt=app.config['SECRET_KEY'])
		print(email)
	except:
		flash('Confirmation link is invalid or expired')
		return redirect(url_for('login'))
	user = DB.find_one(collection="User", query={"email": email})
	if user['confirmed']:
		flash('Account already confirmed. Please login!')
	else:
		DB.update_one(collection="User", filter={"email": email}, data={"$set":{"confirmed": True}})
		flash('Thank you for confirming your email. Please login!')
	return redirect(url_for('login'))

@app.route('/reset-password/<token>', methods=['GET', 'POST']) 
def reset_pwd(token):
	try:
		serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		email = serializer.loads(token, salt=app.config['SECRET_KEY'])
	except:
		flash('Reset link is invalid or expired')
		return redirect(url_for('login'))

	form = PasswordForm()
	if form.validate_on_submit():
		form.password.data = form.password.data.strip()
		user = DB.find_one(collection="User", query={"email": email})
		if user is None:
			flash('Invalid account!')
			return redirect(url_for('login'))
		else:
			new_password = generate_password_hash(form.password.data)
			DB.update_one(collection="User", filter={"email": email}, data={"$set":{"password": new_password}})
			return redirect(url_for('login'))
	return render_template('reset-password-token.html', form=form, token=token, email=email)
