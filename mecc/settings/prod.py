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

####################
# LDAP Settings    #
####################

LDAP_SPORE = 'http://rest-api.u-strasbg.fr/ldapws/description.json'
LDAP_BASE_URL = 'http://ldap-ws.u-strasbg.fr'
LDAP_TOKEN = '{{ldap_token}}'

#########
# STAGE #
#########
STAGE = '{{ goal }}'

##########
# UPLOAD #
##########

# url for logos upload
MEDIA_ROOT = '/nfs/eva/uploads'
# path for pdf files
FILES_UPLOAD_PATH = 'docs/%Y'

#######################
# Email configuration #
#######################
# SERVER_EMAIL = 'root@localhost'
EMAIL_SUBJECT_PREFIX = '[MECC]'
