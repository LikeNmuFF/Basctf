from flask import Blueprint
challenges_bp = Blueprint('challenges', __name__, template_folder='../templates/challenges')
from . import routes
