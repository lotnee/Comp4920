# Helper functions

# takes a list, key, and query
def get_list(toFilterList, key, query):
	i = 0
	l = []
	while i < len(toFilterList):
		if toFilterList[i][key] == query:
			l.append(toFilterList[i])
		i += 1
	return l

# takes a cursor object, key, subkey and query
def get_cursor(cursor_obj, key, subkey, subkey2, query, query2):
	i = 0
	l = []
	while i < cursor_obj.count():
		j = 0
		while j < len(cursor_obj[i][key]):
			if cursor_obj[i][key][j][subkey] == query and cursor_obj[i][key][j][subkey2] == query2:
				l.append(cursor_obj[i])
			j += 1
		i += 1
	return l

# return index
def get_index_2key(arrayList, key, query, key2, query2):
	i = 0
	while i < len(arrayList):
		# print(arrayList[i][key])
		# print(query)
		if arrayList[i][key] == query and arrayList[i][key2] == query2:
			return i
		i += 1
	return -1

# return index for poll
def get_index_1key(arrayList, key, query):
	i = 0
	while i < len(arrayList[key]):
		# print(arrayList[i][key])
		print(query)
		print(arrayList[key][i]['date'])
		if arrayList[key][i]['date'] == query:
			return i
		i += 1
	return -1

# --- DB utility function 
from app.database import DB

# get list of documents by object id
def get_list_of_documents(obj_id_list, collection):
	documentList = []
	for obj_id in obj_id_list:
		document = DB.find_one(collection=collection, query={'_id':obj_id})
		documentList.append(document)
	return documentList

# --- mail utility function
from app import app, mail
from flask import url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

def confirmation_email(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	url = url_for('confirm_email', token = serializer.dumps(email, salt=app.config['SECRET_KEY']), _external=True)
	html = render_template('confirmation-email.html', confirm_url=url)
	print(f'\n CLICK ME \n {email}\'s confirmation url -> {url}\n')
	# won't send since i am no a free tier can't share inbox
	# so check terminal and click on the confirmation url
	send_email('Confirm your email address', [email], html)

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    mail.send(msg)


from app.database import DB
def get_name(email):
	return DB.find_one(collection = "Profile", query = {"email":email}, projection = {"firstName": 1, "lastName" : 1})
