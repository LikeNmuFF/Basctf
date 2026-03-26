from flask import Blueprint
scoreboard_bp = Blueprint('scoreboard', __name__, template_folder='../templates/scoreboard')
from . import routes
