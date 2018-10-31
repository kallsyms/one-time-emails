from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config.from_object('web.config.Config')

Bootstrap(app)
CSRFProtect(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from web.auth.views import auth
from web.mail.views import mail
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(mail)

db.create_all()
