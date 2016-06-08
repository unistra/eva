# -*- coding: utf-8 -*-

from os import environ
from os.path import normpath
from .base import *

#######################
# Debug configuration #
#######################

DEBUG = True


##########################
# Database configuration #
##########################

# In your virtualenv, edit the file $VIRTUAL_ENV/bin/postactivate and set
# properly the environnement variable defined in this file (ie: os.environ[KEY])
# ex: export DEFAULT_DB_NAME='project_name'

# Default values for default database are :
# engine : sqlite3
# name : PROJECT_ROOT_DIR/default.db


DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = 'mecc.db'


#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = environ.get('LOG_DIR',
        normpath(join('/tmp', '%s.log' % SITE_NAME)))
LOGGING['handlers']['file']['level'] = 'DEBUG'

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'DEBUG'


###########################
# Unit test configuration #
###########################

INSTALLED_APPS += (
    'coverage',
    'debug_toolbar',
)
TEST_RUNNER = 'django_coverage.coverage_runner.CoverageRunner'

############
# Dipstrap #
############

DIPSTRAP_VERSION = environ.get('DIPSTRAP_VERSION', 'latest')
DIPSTRAP_STATIC_URL += '%s/' % DIPSTRAP_VERSION

#################
# Debug toolbar #
#################

DEBUG_TOOLBAR_PATCH_SETTINGS = False
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
INTERNAL_IPS = ('127.0.0.1', '0.0.0.0')


####################
# Camelot settings #
####################

CAMELOT_SPORE = environ.get('CAMELOT_SPORE', 'http://rest-api.u-strasbg.fr/camelot/description.json')
CAMELOT_BASE_URL = environ.get('CAMELOT_BASE_URL', 'https://camelot-test.u-strasbg.fr')
CAMELOT_TOKEN = environ.get('CAMELOT_TOKEN', 'S3CR3T')



####################
# LDAP Settings    #
####################

LDAP_SPORE = environ.get('LDAP_SPORE', 'http://rest-api.u-strasbg.fr/ldapws/description.json')
LDAP_BASE_URL = environ.get('LDAP_BASE_URL', "http://ldapws-test.u-strasbg.fr")
LDAP_TOKEN = environ.get('LDAP_TOKEN', 'S3CR3T')


#######################
# Email configuration #
#######################
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'localhost'
# SERVER_EMAIL = 'root@{{ server_name }}'
# EMAIL_SUBJECT_PREFIX = '[{{ application_name }}]'
# EMAIL_PORT = 1025

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'root@localhost'
EMAIL_SUBJECT_PREFIX = "MECC"
