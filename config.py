import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SECRET_KEY = '5eea203c0f47c52a4e5cda0fdad0f9dfe669788144c552cac4ade7ce53b8f96f'
BASE_DIR = Path(__file__).resolve().parent


def _default_database_url():
    return 'mysql+pymysql://root:@localhost/ctf_platform'


def _normalize_database_url(raw_url: str | None) -> str:
    database_url = (raw_url or _default_database_url()).strip()
    if database_url.startswith('mysql://'):
        database_url = f'mysql+pymysql://{database_url[len("mysql://"):]}'

    parsed = urlsplit(database_url)
    if parsed.scheme != 'mysql+pymysql':
        return database_url

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    ssl_mode = (query.pop('ssl-mode', '') or query.pop('ssl_mode', '')).upper()

    if ssl_mode == 'REQUIRED':
        ssl_ca = query.get('ssl_ca') or os.environ.get('MYSQL_SSL_CA')
        if not ssl_ca:
            local_ca = BASE_DIR / 'ca.pem'
            if local_ca.exists():
                ssl_ca = str(local_ca)
        if ssl_ca:
            query['ssl_ca'] = ssl_ca

    if 'charset' not in query:
        query['charset'] = 'utf8mb4'

    return urlunsplit(parsed._replace(query=urlencode(query)))


def get_config_name() -> str:
    return os.environ.get('APP_ENV') or os.environ.get('FLASK_ENV') or 'production'


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(os.environ.get('DATABASE_URL'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB upload limit
    UPLOAD_FOLDER = os.environ.get(
        'UPLOAD_FOLDER',
        os.path.join(os.path.dirname(__file__), 'app', 'static', 'uploads'),
    )
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'zip', 'tar', 'gz', 'rar', '7z', 'exe', 'bin', 'pcap', 'sql', 'xml', 'json', 'py', 'js', 'html', 'css'}
    WTF_CSRF_ENABLED = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'ctf_session')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    VERIFY_DB_ON_START = _get_bool_env('VERIFY_DB_ON_START', True)


class DevelopmentConfig(Config):
    DEBUG = True
    VERIFY_DB_ON_START = _get_bool_env('VERIFY_DB_ON_START', False)


class ProductionConfig(Config):
    DEBUG = False
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    TEMPLATES_AUTO_RELOAD = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig,
}
