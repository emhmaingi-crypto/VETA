import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

try:
    import dj_database_url
    _dj_db_url = True
except ImportError:
    _dj_db_url = False

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Build ALLOWED_HOSTS from env, always add Railway public domain if present
_raw_hosts = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(',') if h.strip()]
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# CSRF trusted origins for Railway HTTPS
CSRF_TRUSTED_ORIGINS = []
if _railway_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_domain}')
_extra_csrf = os.environ.get('CSRF_TRUSTED_ORIGINS', '')
for _origin in _extra_csrf.split(','):
    _o = _origin.strip()
    if _o and _o not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_o)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'projects',
    'opportunities',
    'mentorship',
    'scholarships',
    'services',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'veta_connect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'veta_connect.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# On Railway (or any host) use DATABASE_URL if provided
_db_url = os.environ.get('DATABASE_URL', '')
if _db_url and _dj_db_url:
    DATABASES['default'] = dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
        conn_health_checks=True,
    )

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.StudentUser'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
