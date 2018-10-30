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

DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'
DATABASES['default']['NAME'] = normpath(join(dirname(dirname(SITE_ROOT)), 'shared/default.db'))

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '.u-strasbg.fr',
    '.unistra.fr',
]

#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = '{{ remote_current_path }}/log/app.log'

for logger in LOGGING['loggers']:
    LOGGING['loggers'][logger]['level'] = 'DEBUG'

############
# Dipstrap #
############

DIPSTRAP_VERSION = '{{ dipstrap_version }}'
DIPSTRAP_STATIC_URL += '%s/' % DIPSTRAP_VERSION

####################
# LDAP Settings    #
####################

LDAP_SPORE = environ.get('LDAP_SPORE', 'http://rest-api.u-strasbg.fr/ldapws/description.json')
LDAP_BASE_URL = environ.get('LDAP_BASE_URL', "http://ldapws-test.u-strasbg.fr")
LDAP_TOKEN = '{{ldap_token}}'

####################
# EMAIL Settings   #
####################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'root@{{ server_name }}'
EMAIL_SUBJECT_PREFIX = '[MECC]'
EMAIL_TEST = ['ibis.ismail@unistra.fr', 'weible@unistra.fr', 'baguet@unistra.fr'] # For test purpose comment if not needed
# EMAIL_PORT = 1025

#########
# STAGE #
#########

STAGE = '{{ goal }}'

############################
# Ceph Storage credentials #
############################
CEPH_STORAGE_KEY_ID = '{{ ceph_key_id }}'
CEPH_STORAGE_SECRET_KEY = '{{ ceph_secret_key }}'
CEPH_STORAGE_ENDPOINT_URL = '{{ ceph_endpoint_url }}'
CEPH_STORAGE_BUCKET = '{{ ceph_bucket }}'

##########
# Celery #
##########

RABBITMQ_USER = '{{ application_name }}'
RABBITMQ_PASSWORD = '{{ rabbitmq_password }}'
RABBITMQ_SERVER = '{{ rabbitmq_server }}'
RABBITMQ_VHOST = '{}_test'.format(RABBITMQ_USER)
BROKER_URL = "amqp://{}:{}@{}/{}".format(
    RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_SERVER, RABBITMQ_VHOST
)
