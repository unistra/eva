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

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '*'
]

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
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

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
EMAIL_SUBJECT_PREFIX = '[MECC]'
EMAIL_TEST = ['ibis.ismail@unistra.fr', 'weible@unistra.fr', 'baguet@unistra.fr']  # For test purpose comment if not needed

#########
# STAGE #
#########

STAGE = 'dev'

############################
# Ceph Storage credentials #
############################
CEPH_STORAGE_KEY_ID = environ.get('CEPH_KEY_ID')
CEPH_STORAGE_SECRET_KEY = environ.get('CEPH_SECRET_KEY')
CEPH_STORAGE_ENDPOINT_URL = environ.get('CEPH_ENDPOINT_URL', 'https://s3.unistra.fr')
CEPH_STORAGE_BUCKET = environ.get('CEPH_BUCKET')

##########
# CELERY #
##########
RABBITMQ_USER = environ.get('RABBITMQ_USER')
RABBITMQ_PASSWORD = environ.get('RABBITMQ_PASSWORD')
RABBITMQ_SERVER = environ.get('RABBITMQ_SERVER')
RABBITMQ_VHOST = environ.get('RABBITMQ_VHOST')
BROKER_URL = "amqp://{}:{}@{}/{}".format(
    RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_SERVER, RABBITMQ_VHOST
)
