# -*- coding: utf-8 -*-

from os.path import abspath, basename, dirname, join, normpath


######################
# Path configuration #
######################

DJANGO_ROOT = dirname(dirname(abspath(__file__)))
SITE_ROOT = dirname(DJANGO_ROOT)
SITE_NAME = basename(DJANGO_ROOT)


#######################
# Debug configuration #
#######################

DEBUG = False
TEMPLATE_DEBUG = DEBUG


##########################
# Manager configurations #
##########################

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY]
# ex: export LDAP_DB_USER='uid=toto,ou=uds,ou=people,o=annuaire

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/mecc.db

# defaut db connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mecc',                      # Or path to database file if using sqlite3.
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',                      # Set to empty string for default.
    }
}


######################
# Site configuration #
######################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    '.u-strasbg.fr',
    '.unistra.fr',
    '127.0.0.1',
]

#########################
# General configuration #
#########################

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr-FR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True


#######################
# locale configuration #
#######################

LOCALE_PATHS = (normpath(join(DJANGO_ROOT, 'locale')),)


#######################
# Media configuration #
#######################

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = normpath(join(DJANGO_ROOT, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'


##############################
# Static files configuration #
##############################

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/site_media/'

# Additional locations of static files
STATICFILES_DIRS = (
    normpath(join(DJANGO_ROOT, 'static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


############
# Dipstrap #
############

DIPSTRAP_STATIC_URL = '//django-static.u-strasbg.fr/dipstrap/'


##############
# Secret key #
##############

# Make this unique, and don't share it with anybody.
# Only for dev and test environnement. Should be redefined for production
# environnement
SECRET_KEY = 'ma8r116)33!-#pty4!sht8tsa(1bfe%(+!&9xfack+2e9alah!'


##########################
# Template configuration #
##########################
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    normpath(join(DJANGO_ROOT, 'templates')),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'mecc.apps.utils.context_processors.sidebar'
)


############################
# Middleware configuration #
############################

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django_cas.middleware.CASMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'mecc.middleware.UsefullDisplay',

)


#####################
# Url configuration #
#####################

ROOT_URLCONF = '%s.urls' % SITE_NAME


######################
# WSGI configuration #
######################

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME


#############################
# Application configuration #
#############################

DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin'
    # 'django.contrib.admindocs',
)

THIRD_PARTY_APPS = (
    'crispy_forms',
    'django_cas',
    'ckeditor',
    'django_celery_results',
)

LOCAL_APPS = (
    'mecc.apps.utils',
    'mecc',
    'mecc.apps.doc_gen',
    'mecc.apps.commission',
    'mecc.apps.degree',
    'mecc.apps.institute',
    'mecc.apps.years',
    'mecc.apps.adm',
    'mecc.apps.rules',
    'mecc.apps.training',
    'mecc.apps.mecctable',
    'mecc.apps.files',
    'mecc.apps.travail',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


#########################
# Session configuration #
#########################

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

#####################
# Log configuration #
#####################

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(name)s:%(lineno)s %(message)s'
         }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '',
            'maxBytes': 209715200,
            'backupCount': 3,
            'formatter': 'default'
        },
        # 'console': {
        #     'class': 'logging.StreamHandler',
        # },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO'
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'mecc': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': True
        },
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        #     'handlers': ['console'],
        # }
    }
}


# ### Custom users stuff######"

# ## CRISPY STUFF ## #
CRISPY_TEMPLATE_PACK = 'bootstrap3'


##################
# Authentication #
##################

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas.backends.CASBackend',
)


SESSION_EXPIRE_AT_BROWSER_CLOSE = True


CKEDITOR_CONFIGS = {
    'default': {
        # 'skin': 'minimalist',
        'skin': 'office2013',
        'toolbar_Basic': [
            ['-', 'Bold', 'Italic', ]
        ],
        'toolbar_Tools': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo', 'PasteFromWord', ]},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', ]},
            {'name': 'paragraph', 'items': ['BulletedList', ]},
            # {'name': 'styles', 'items': ['Font', 'FontSize', ]},
            # {'name': 'colors', 'items': ['TextColor', 'BGColor', ]},
            {'name': 'tools', 'items': ['Maximize', ]},
        ],
        'toolbar': 'Tools',
        'height': '9em',
        'width': '100%',
        'entities_latin': 'false',
        'entities': 'false',
        'extraPlugins': ','.join([
            'pastefromword',
        ]),
    },
}

HTML_SANITIZERS = {
    'rules': {
        'tags': {
            'abbr', 'acronym',
            'b', 'br',
            'em',
            'i',
            'li',
            'ol',
            'p',
            'sub', 'sup', 'strong',
            'u', 'ul',
        },
        'attributes': {},
        'empty': {
            'br',
        },
        'separate': {
            'li', 'p',
        }
    }
}


############################
# CAS server configuration #
############################

CAS_SERVER_URL = 'https://cas.unistra.fr:443/cas/login'
CAS_LOGOUT_REQUEST_ALLOWED = ('cas-dev1.u-strasbg.fr', 'cas-dev2.u-strasbg.fr')
CAS_USER_CREATION = True
CAS_USERNAME_FORMAT = lambda username: username.lower().strip()

############
# apogeews #
############

APOGEEWS_SPORE = None
APOGEEWS_BASE_URL = None
APOGEEWS_TOKEN = None

########
# MAIL #
########

MAIL_FROM = 'des-admin-mecc@unistra.fr'
MAIL_ARCHIVES = 'des-mecc-archives@unistra.fr'


#########
# FILES #
#########

FILES_UPLOAD_PATH = 'uploads/docs/%Y'

##########
# CELERY #
##########

CELERY_NAME = "mecc"
CELERY_RESULT_BACKEND = "django-db"
BROKER_URL = ""
