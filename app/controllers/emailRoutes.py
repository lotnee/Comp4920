from app import app, mail
from app.database import DB
from itsdangerous import URLSafeTimedSerializer
from flask import flash, redirect, url_for

@app.route('/confirm/<token>')
def confirm_email(token):
	try:
		serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
		email = serializer.loads(token, salt=app.config['SECRET_KEY'])
		print(email)
	except:
		flash('Confirmation link is invalied or expired')
		return redirect(url_for('login'))
	user = DB.find_one(collection="User", query={"email": email})
	if user['confirmed']:
		flash('Account already confirmed. Please login!')
	else:
		DB.update_one(collection="User", filter={"email": email}, data={"$set":{"confirmed": True}})
		flash('Thank you for confirming your email. Please login!')
	return redirect(url_for('login'))


