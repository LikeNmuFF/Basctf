from functools import wraps
from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from . import admin_bp
from .forms import ChallengeForm, EditChallengeForm
from ..models import Challenge, User, Solve, HintUsage
from ..extensions import db
from ..utils import hash_flag, save_upload, normalize_external_link


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_challenges = Challenge.query.count()
    total_solves = Solve.query.count()
    challenges = Challenge.query.order_by(Challenge.created_at.desc()).all()
    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_challenges=total_challenges,
                           total_solves=total_solves,
                           challenges=challenges)


@admin_bp.route('/challenges/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_challenge():
    form = ChallengeForm()
    if form.validate_on_submit():
        file_path = None
        if form.attachment.data:
            file_path = save_upload(form.attachment.data)

        challenge = Challenge(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            difficulty=form.difficulty.data,
            points=form.points.data,
            link=normalize_external_link(form.link.data),
            hint_1=form.hint_1.data,
            hint_2=form.hint_2.data,
            hint_3=form.hint_3.data,
            flag_hash=hash_flag(form.flag.data),
            file_path=file_path
        )
        db.session.add(challenge)
        db.session.commit()
        flash(f'Challenge "{challenge.title}" created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin_new_challenge.html', form=form)


@admin_bp.route('/challenges/<int:challenge_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    form = EditChallengeForm(obj=challenge)
    if form.validate_on_submit():
        challenge.title = form.title.data
        challenge.description = form.description.data
        challenge.category = form.category.data
        challenge.difficulty = form.difficulty.data
        challenge.points = form.points.data
        challenge.link = normalize_external_link(form.link.data)
        challenge.hint_1 = form.hint_1.data
        challenge.hint_2 = form.hint_2.data
        challenge.hint_3 = form.hint_3.data
        if form.flag.data:
            challenge.flag_hash = hash_flag(form.flag.data)
        if form.attachment.data:
            new_path = save_upload(form.attachment.data)
            if new_path:
                challenge.file_path = new_path
        db.session.commit()
        flash('Challenge updated.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin_edit_challenge.html', form=form, challenge=challenge)


@admin_bp.route('/challenges/<int:challenge_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    challenge.is_active = not challenge.is_active
    db.session.commit()
    status = 'activated' if challenge.is_active else 'deactivated'
    flash(f'Challenge "{challenge.title}" {status}.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/challenges/<int:challenge_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    title = challenge.title  # capture before deletion

    # Remove dependent rows to satisfy foreign key constraints
    HintUsage.query.filter_by(challenge_id=challenge_id).delete()
    Solve.query.filter_by(challenge_id=challenge_id).delete()

    db.session.delete(challenge)
    db.session.commit()
    flash(f'Challenge "{title}" deleted.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.score.desc()).all()
    return render_template('admin_users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't modify your own admin status.", 'danger')
        return redirect(url_for('admin.users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'Admin status updated for {user.username}.', 'info')
    return redirect(url_for('admin.users'))
