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

CAMELOT_SPORE = 'http://rest-api.u-strasbg.fr/camelot/description.json'
CAMELOT_BASE_URL = "https://camelot-test.u-strasbg.fr"
CAMELOT_TOKEN = "f8a635587c1cf39826fbd9aabfeab35107cd54b8"



####################
# LDAP Settings    #
####################

LDAP_SPORE = 'http://rest-api.u-strasbg.fr/ldapws/description.json'
LDAP_BASE_URL = "http://ldapws-test.u-strasbg.fr"
LDAP_TOKEN = "d800c7d0ed5f38b66b6a5a1fe804f0dff500d236"
