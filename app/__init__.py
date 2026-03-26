from flask import Flask
from .extensions import csrf, db, login_manager
from config import DEFAULT_SECRET_KEY, config


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    if not app.debug and app.config.get('SECRET_KEY') == DEFAULT_SECRET_KEY:
        raise ValueError('SECRET_KEY must be set to a unique value in production.')
    

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .challenges import challenges_bp
    app.register_blueprint(challenges_bp, url_prefix='/challenges')

    from .scoreboard import scoreboard_bp
    app.register_blueprint(scoreboard_bp, url_prefix='/scoreboard')

    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Main index route
    from flask import render_template, request
    from sqlalchemy import func
    from .models import User, Challenge, Solve
    
    @app.route('/')
    def index():
        # Calculate platform stats
        total_challenges = Challenge.query.count()
        total_players = User.query.count()
        total_solves = Solve.query.count()
        
        # Calculate completion percentage
        if total_players > 0 and total_challenges > 0:
            max_possible_solves = total_players * total_challenges
            completion_percentage = int((total_solves / max_possible_solves) * 100) if max_possible_solves > 0 else 0
        else:
            completion_percentage = 0
        
        # Count unique categories
        total_categories = db.session.query(Challenge.category).distinct().count()
        
        stats = {
            'challenges': total_challenges,
            'players': total_players,
            'completion': completion_percentage,
            'categories': total_categories
        }
        
        return render_template('landing.html', stats=stats)

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

    # Create database tables and ensure new hint columns exist
    with app.app_context():
        db.create_all()
        _ensure_hint_columns()

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
