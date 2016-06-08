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
# Camelot settings #
####################

CAMELOT_SPORE = environ.get('CAMELOT_SPORE', 'http://rest-api.u-strasbg.fr/camelot/description.json')
CAMELOT_BASE_URL = environ.get('CAMELOT_BASE_URL', 'https://camelot-test.u-strasbg.fr')
CAMELOT_TOKEN = environ.get('CAMELOT_TOKEN', 'S3CR3T')



####################
# LDAP Settings    #
####################

LDAP_SPORE = environ.get('CAMELOT_SPORE', 'http://rest-api.u-strasbg.fr/ldapws/description.json')
LDAP_BASE_URL = environ.get('CAMELOT_BASE_URL', "http://ldapws-test.u-strasbg.fr")
LDAP_TOKEN = environ.get('CAMELOT_TOKEN', 'S3CR3T')


####################
# EMAIL Settings   #
####################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
SERVER_EMAIL = 'root@{{ server_name }}'
EMAIL_SUBJECT_PREFIX = '[{{ application_name }}]'
# EMAIL_PORT = 1025
