""" Main blueprint creation. """
# Routes are imported at the bottom after blue print creation to avoid circular dependancies.

from flask import Blueprint
from ..models import Permission

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
    
# Relative import (current package).
from . import views, errors   # Importing the routes inorder to associate them with blueprint.