from datetime import datetime, timedelta
from math import ceil
from urllib.parse import urljoin, urlsplit

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import or_

from . import auth_bp
from .forms import LoginForm, RegistrationForm
from ..challenges.services import get_submission_stats_for_user
from ..extensions import db
from ..models import LoginAttempt, User

MAX_LOGIN_ATTEMPTS = 5
LOGIN_COOLDOWN_SECONDS = 60


def _client_ip() -> str:
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()[:45]
    return (request.remote_addr or 'unknown')[:45]


def _is_safe_next_url(target: str | None) -> bool:
    if not target:
        return False
    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(urljoin(request.host_url, target))
    return (
        test_url.scheme in {'http', 'https'}
        and ref_url.netloc == test_url.netloc
    )


def _get_login_cooldown_remaining(username: str, ip_address: str) -> int:
    cutoff = datetime.utcnow() - timedelta(seconds=LOGIN_COOLDOWN_SECONDS)
    recent_attempts = LoginAttempt.query.filter(
        LoginAttempt.attempted_at >= cutoff,
        LoginAttempt.is_success.is_(False),
        or_(LoginAttempt.username == username, LoginAttempt.ip_address == ip_address),
    ).order_by(LoginAttempt.attempted_at.desc()).all()

    if len(recent_attempts) < MAX_LOGIN_ATTEMPTS:
        return 0

    latest_attempt = recent_attempts[0]
    remaining = ceil((latest_attempt.attempted_at + timedelta(seconds=LOGIN_COOLDOWN_SECONDS) - datetime.utcnow()).total_seconds())
    return max(0, remaining)


def _record_login_attempt(username: str, ip_address: str, is_success: bool) -> None:
    db.session.add(LoginAttempt(username=username, ip_address=ip_address, is_success=is_success))
    db.session.commit()


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list_challenges'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list_challenges'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        ip_address = _client_ip()
        cooldown_remaining = _get_login_cooldown_remaining(username, ip_address)
        if cooldown_remaining > 0:
            flash(f'Too many login attempts. Wait {cooldown_remaining} seconds and try again.', 'danger')
            return render_template('login.html', form=form), 429

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(form.password.data):
            _record_login_attempt(username, ip_address, True)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            if not _is_safe_next_url(next_page):
                next_page = url_for('challenges.list_challenges')
            return redirect(next_page)
        _record_login_attempt(username, ip_address, False)
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/stats')
@login_required
def stats():
    stats_summary = get_submission_stats_for_user(current_user.id)
    return render_template('stats.html', stats_summary=stats_summary)
