from flask import Flask
from app.database import DB
from flask_login import LoginManager
from flask_mail import Mail
import os

absolute_path = os.path.abspath(os.path.dirname(__file__))
# print(absolute_path)
# print(os.path.exists("app/static/images/male.jpg"))
app = Flask(__name__)
DB.init()
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(absolute_path, 'static/images')
app.config['SECRET_KEY'] = 'i-just-want-to-graduate'

login_manager = LoginManager(app)

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'ed04aff2920f56'
app.config['MAIL_PASSWORD'] = '1f02644fbbd942'
app.config['MAIL_DEFAULT_SENDER'] = 'mail@hangouts'
app.config['MAIL_SUPPRESS_SEND'] = True # change this to true to actually send

mail = Mail(app)

# from app.controllers import routes
from app.controllers import userRoutes
from app.controllers import profileRoutes
from app.controllers import friendRoutes
from app.controllers import eventRoutes
from app.controllers import searchRoutes
from app.controllers import emailRoutes
from app.controllers import pollRoutes