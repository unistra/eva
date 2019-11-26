# -*- coding: utf-8 -*-

from os import environ
from os.path import normpath
from .base import *

##########################
# Database configuration #
##########################

DATABASES['default']['HOST'] = '{{ default_db_host }}'
DATABASES['default']['USER'] = '{{ default_db_user }}'
DATABASES['default']['PASSWORD'] = '{{ default_db_password }}'
DATABASES['default']['NAME'] = '{{ default_db_name }}'

############################
# Allowed hosts & Security #
############################

ALLOWED_HOSTS = [
    '.u-strasbg.fr',
    '.unistra.fr',
]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'ssl')

#####################
# Log configuration #
#####################

LOGGING['handlers']['file']['filename'] = '{{ remote_current_path }}/log/app.log'

##############
# Secret key #
##############

SECRET_KEY = '{{ secret_key }}'

############
# Dipstrap #
############

DIPSTRAP_VERSION = '{{ dipstrap_version }}'
DIPSTRAP_STATIC_URL += '%s/' % DIPSTRAP_VERSION

#########
# STAGE #
#########

STAGE = '{{ goal }}'

##########
# UPLOAD #
##########

# url for logos upload
MEDIA_ROOT = '/nfs/mecc/uploads'
# path for pdf files
FILES_UPLOAD_PATH = 'docs/%Y'

####################
# LDAP Settings    #
####################

LDAP_SPORE = environ.get('LDAP_SPORE', 'http://rest-api.u-strasbg.fr/ldapws/description.json')
LDAP_BASE_URL = environ.get('LDAP_BASE_URL', "http://ldap-ws.u-strasbg.fr")
LDAP_TOKEN = '{{ldap_token}}'

#######################
# Email configuration #
#######################
#SERVER_EMAIL = 'root@localhost'
EMAIL_SUBJECT_PREFIX = '[MECC]'

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
RABBITMQ_VHOST = '{}_preprod'.format(RABBITMQ_USER)
BROKER_URL = "amqp://{}:{}@{}/{}".format(
    RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_SERVER, RABBITMQ_VHOST
)

##########
# SENTRY #
##########
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://38db3389420c4cc6b544a4c50c150569@sentry-test.app.unistra.fr/11",
    integrations=[DjangoIntegration()],
    environment='preprod',
)
