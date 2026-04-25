import os
import logging
from pathlib import Path

from flask import Flask
from sqlalchemy import text
from werkzeug.middleware.proxy_fix import ProxyFix

from .extensions import csrf, db, login_manager
from config import DEFAULT_SECRET_KEY, config


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
    _configure_logging(app)

    if not app.debug and app.config.get('SECRET_KEY') == DEFAULT_SECRET_KEY:
        raise ValueError('SECRET_KEY must be set to a unique value in production.')

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .challenges import challenges_bp
    app.register_blueprint(challenges_bp, url_prefix='/challenges')

    from .scoreboard import scoreboard_bp
    app.register_blueprint(scoreboard_bp, url_prefix='/scoreboard')

    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from .activity import activity_bp
    app.register_blueprint(activity_bp, url_prefix='/activity')

    from flask import render_template, request
    from .models import Challenge, Solve, User
    from .utils import get_user_ranking, format_ranking_position

    @app.context_processor
    def utility_processor():
        return {
            'get_user_ranking': get_user_ranking,
            'format_ranking_position': format_ranking_position,
        }

    @app.route('/')
    def index():
        total_challenges = Challenge.query.count()
        total_players = User.query.count()
        total_solves = Solve.query.count()

        if total_players > 0 and total_challenges > 0:
            max_possible_solves = total_players * total_challenges
            completion_percentage = int((total_solves / max_possible_solves) * 100) if max_possible_solves > 0 else 0
        else:
            completion_percentage = 0

        total_categories = db.session.query(Challenge.category).distinct().count()

        stats = {
            'challenges': total_challenges,
            'players': total_players,
            'completion': completion_percentage,
            'categories': total_categories,
        }

        return render_template('landing.html', stats=stats)

    @app.route('/healthz')
    def healthz():
        db.session.execute(text('SELECT 1'))
        return {'status': 'ok'}, 200

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return render_template(
            'errors/405.html',
            allowed_methods=getattr(error, 'valid_methods', None),
            attempted_method=request.method,
        ), 405

    with app.app_context():
        if app.config.get('VERIFY_DB_ON_START'):
            _verify_database_connection(app)
        db.create_all()
        _ensure_hint_columns()
        _bootstrap_admin_user()

    return app


def _ensure_hint_columns():
    from sqlalchemy import text

    columns = {
        'hint_1': 'TEXT',
        'hint_2': 'TEXT',
        'hint_3': 'TEXT',
        'link': 'VARCHAR(500)',
        'difficulty': 'VARCHAR(16) NOT NULL DEFAULT "medium"',
    }

    inspector = __import__('sqlalchemy').inspect(db.engine)
    existing = {c['name'] for c in inspector.get_columns('challenges')}
    added = set()

    with db.engine.begin() as conn:
        for name, col_type in columns.items():
            if name not in existing:
                try:
                    conn.execute(text(f'ALTER TABLE challenges ADD COLUMN {name} {col_type}'))
                    added.add(name)
                except Exception as e:
                    print(f'Warning: failed to add column {name}: {e}')

        if 'difficulty' in existing or 'difficulty' in added:
            try:
                conn.execute(text('UPDATE challenges SET difficulty = "medium" WHERE difficulty IS NULL'))
            except Exception as e:
                print(f'Warning: failed to backfill difficulty: {e}')


def _bootstrap_admin_user():
    from .models import User

    username = os.environ.get('ADMIN_USERNAME', '').strip()
    email = os.environ.get('ADMIN_EMAIL', '').strip()
    password = os.environ.get('ADMIN_PASSWORD', '').strip()

    if not all([username, email, password]):
        return

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        if not existing_user.is_admin:
            existing_user.is_admin = True
            db.session.commit()
        return

    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()


def _configure_logging(app):
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'), logging.INFO)
    app.logger.setLevel(log_level)
    if not app.debug:
        for handler in app.logger.handlers:
            handler.setLevel(log_level)


def _verify_database_connection(app):
    try:
        db.session.execute(text('SELECT 1'))
        app.logger.info('Database connectivity check passed.')
    except Exception:
        app.logger.exception('Database connectivity check failed during startup.')
        raise
