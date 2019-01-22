import os
import dj_database_url

# Global default switch. Default is True
# env: $DJANGO_DEBUG
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ['true', '1', 'yes']

# Host that django will listen to
# env: $DJANGO_HOST specifies additional hosts for django, comma separated
ALLOWED_HOSTS = ['localhost', '127.0.0.1'] + [x.strip() for x in os.environ.get('DJANGO_HOST', '').split(',')]

# [REQUIRED] The secret key to generate tokens
# env: $DJANGO_SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '!!!!CHANGE_ME!!!!')

""" Database connection is specified by url from env $DJANGO_DB_URL:
    Examples:
        postgres://USER:PASSWORD@HOST:PORT/NAME
        mysql://USER:PASSWORD@HOST:PORT/NAME
        sqlite:////full/path/to/your/database/file.sqlite
"""
DATABASES = {
    'default': dj_database_url.config('DJANGO_DB_URL',
                                      default='sqlite:///db.sqlite3',
                                      conn_max_age=int(os.environ.get('DJANGO_DB_CONN_MAX_AGE', '600')))
}


# Application definition
INSTALLED_APPS = [
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = os.environ.get('DJANGO_LANGUAGE_CODE', 'ru-RU')
TIME_ZONE = os.environ.get('DJANGO_TIME_ZONE', 'UTC')
USE_I18N = True
USE_L10N = True
USE_TZ = True

AUTH_USER_MODEL = 'app.Profile'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
# [REQUIRED] $DJANGO_STATIC_ROOT - path to store static files
STATIC_ROOT = os.environ.get('DJANGO_STATIC_ROOT')
STATIC_URL = '/static/'

# [REQUIRED] DJANGO_MEDIA_ROOT - path to store media/user created files
MEDIA_ROOT = os.environ.get('DJANGO_MEDIA_ROOT')
MEDIA_URL = '/media/'

SCREENSHOT_SIZE = 150

EDITABLE_FILE_TYPES = [
    "application/javascript",
    "application/json",
    "application/atom+xml",
    "application/rss+xml",
    "application/xml",
    "application/sparql-query",
    "application/sparql-results+xml",
    "text/calendar",
    "text/css",
    "text/csv",
    "text/html",
    "text/n3",
    "text/plain",
    "text/plain-bas",
    "text/prs.lines.tag",
    "text/richtext",
    "text/sgml",
    "text/tab-separated-values",
    "text/troff",
    "text/turtle",
    "text/uri-list",
    "text/vnd.curl",
    "text/vnd.curl.dcurl",
    "text/vnd.curl.mcurl",
    "text/vnd.curl.scurl",
    "text/vnd.fly",
    "text/vnd.fmi.flexstor",
    "text/vnd.graphviz",
    "text/vnd.in3d.3dml",
    "text/vnd.in3d.spot",
    "text/vnd.sun.j2me.app-descriptor",
    "text/vnd.wap.wml",
    "text/vnd.wap.wmlscript",
    "text/x-asm",
    "text/x-c",
    "text/x-fortran",
    "text/x-java-source,java",
    "text/x-pascal",
    "text/x-setext",
    "text/x-uuencode",
    "text/x-vcalendar",
    "text/x-vcard",
    "text/yaml",
]
