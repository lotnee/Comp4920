from flask import Flask
from app.database import DB
from flask_login import LoginManager
import os

absolute_path = os.path.abspath(os.path.dirname(__file__))
# print(absolute_path)
# print(os.path.exists("app/static/images/male.jpg"))
app = Flask(__name__)
DB.init()
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(absolute_path, 'static/images')
app.config['SECRET_KEY'] = 'i-just-want-to-graduate'
login_manager = LoginManager(app)

# from app.controllers import routes
from app.controllers import userRoutes
from app.controllers import profileRoutes
from app.controllers import friendRoutes
from app.controllers import eventRoutes
from app.controllers import searchRoutes
