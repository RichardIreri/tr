""" Flask-HTTPAuth verification. """

from . import api
from flask_httpauth import HTTPBasicAuth
from ..models import User
from flask import g, jsonify
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()  # Creating an object of class HTTPBasicAuth

# Callback function that contains the verification information;
# Improved authentication verfication token support.
@auth.verify_password
def verify_password(email_or_token, passward):
    if email_or_token == '':
        return False 
    if passward == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used =False
    return user.verify_password(passward)

# Flask-HTTPAuth error handler
@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

#@api.route('/posts/')
#@auth.login_required
#def get_posts():
#    pass

# Before_request handler with authentication
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

# Authentication token generation route
@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})