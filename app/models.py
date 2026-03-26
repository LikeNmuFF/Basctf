from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    score = db.Column(db.Integer, default=0, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    solves = db.relationship('Solve', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    flag_submissions = db.relationship(
        'FlagSubmission',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Challenge(db.Model):
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag_hash = db.Column(db.String(64), nullable=False)  # SHA256 hex = 64 chars
    points = db.Column(db.Integer, nullable=False, default=100)
    category = db.Column(db.String(64), nullable=False, default='misc')
    difficulty = db.Column(db.String(16), nullable=False, default='medium')
    file_path = db.Column(db.String(256), nullable=True)
    link = db.Column(db.String(500), nullable=True)
    hint_1 = db.Column(db.Text, nullable=True)
    hint_2 = db.Column(db.Text, nullable=True)
    hint_3 = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    solves = db.relationship('Solve', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')
    flag_submissions = db.relationship(
        'FlagSubmission',
        backref='challenge',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    @property
    def solve_count(self):
        return self.solves.count()

    def __repr__(self):
        return f'<Challenge {self.title}>'


class Solve(db.Model):
    __tablename__ = 'solves'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    solved_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge'),
    )

    def __repr__(self):
        return f'<Solve user={self.user_id} challenge={self.challenge_id}>'


class HintUsage(db.Model):
    __tablename__ = 'hint_usage'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    used_hints = db.Column(db.Integer, default=0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_id', name='unique_user_challenge_hint_usage'),
    )

    def __repr__(self):
        return f'<HintUsage user={self.user_id} challenge={self.challenge_id} used_hints={self.used_hints}>'


class FlagSubmission(db.Model):
    __tablename__ = 'flag_submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    is_correct = db.Column(db.Boolean, default=False, nullable=False, index=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return (
            f'<FlagSubmission user={self.user_id} '
            f'challenge={self.challenge_id} correct={self.is_correct}>'
        )


class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    is_success = db.Column(db.Boolean, default=False, nullable=False, index=True)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return (
            f'<LoginAttempt username={self.username} '
            f'ip={self.ip_address} success={self.is_success}>'
        )


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
