from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wot_hub.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
migrate = Migrate()
