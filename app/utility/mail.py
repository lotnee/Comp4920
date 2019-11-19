# --- mail utility function
from app import app, mail
from flask import url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def send_confirmation_email(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	url = url_for('confirm_email', token = serializer.dumps(email, salt=app.config['SECRET_KEY']), _external=True)
	html = render_template('confirmation-email.html', confirm_url=url)
	print(f'\n CLICK ME \n {email}\'s confirmation url -> {url}\n')
	# won't send since i am no a free tier can't share inbox
	# so check terminal and click on the confirmation url
	send_email('Confirm your email address', [email], html)

def send_reset_password(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	url = url_for('reset_pwd', token = serializer.dumps(email, salt=app.config['SECRET_KEY']), _external=True)
	html = render_template('reset-password-email.html', confirm_url=url)
	print(f'\n CLICK ME \n {email}\'s password reset url -> {url}\n')
	# won't send since i am no a free tier can't share inbox
	# so check terminal and click on the confirmation url
	send_email('Reset your password', [email], html)

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    mail.send(msg)
