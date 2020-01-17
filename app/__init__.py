""" Application package constructor. """

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
pagedown = PageDown()

# Application factory function
def create_app(config_name):
    app = Flask(__name__)                             # Creating the application and configuration.
    app.config.from_object(config[config_name])       # Importing the configuration class settings.
    config[config_name].init_app(app)                 # More complex configuration.

    # Extension initialization
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # Redirecting all requests to secure HHTP
    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    # Main blueprint registration.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Authentication blueprint registration
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # API blueprint registration
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    # Attach routes and custome error pages here

    return app                                       # Return the created application instance.