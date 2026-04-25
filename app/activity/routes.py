from flask import render_template
from flask_login import login_required
from . import activity_bp
from ..models import Solve, User, Challenge


@activity_bp.route('/')
@login_required
def activity():
    # Get recent solves with user and challenge information
    # Only show solves from active challenges that users can access
    recent_solves = Solve.query.join(User).join(Challenge).filter(
        Challenge.is_active == True
    ).order_by(
        Solve.solved_at.desc()
    ).limit(50).all()  # Show last 50 solves
    
    return render_template('activity.html', solves=recent_solves)