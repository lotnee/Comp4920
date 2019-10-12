from flask import Flask
from app.database import DB
from flask_login import LoginManager

app = Flask(__name__)
DB.init()
app.config['SECRET_KEY'] = 'i-just-want-to-graduate'
login_manager = LoginManager(app)

from app.controllers import routes