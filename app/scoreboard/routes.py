from flask import render_template
from flask_login import login_required
from . import scoreboard_bp
from ..models import User


@scoreboard_bp.route('/')
@login_required
def scoreboard():
    players = User.query.filter_by(is_admin=False).order_by(
        User.score.desc(), User.created_at.asc()
    ).all()
    return render_template('scoreboard.html', players=players)
