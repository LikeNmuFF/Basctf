from flask import Blueprint

activity_bp = Blueprint('activity', __name__, template_folder='templates')

from . import routes