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
# Camelot settings #
####################

CAMELOT_SPORE = environ.get('CAMELOT_SPORE', 'http://rest-api.u-strasbg.fr/camelot/description.json')
CAMELOT_BASE_URL = environ.get('CAMELOT_BASE_URL', 'https://camelot-test.u-strasbg.fr')
CAMELOT_TOKEN = '{{camelot_token}}'

####################
# LDAP Settings    #
####################

LDAP_SPORE = environ.get('LDAP_SPORE', 'http://rest-api.u-strasbg.fr/ldapws/description.json')
LDAP_BASE_URL = environ.get('LDAP_BASE_URL', "http://ldapws-test.u-strasbg.fr")
LDAP_TOKEN = '{{ldap_token}}'