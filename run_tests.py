# -*- coding: utf-8 -*-

import os
import sys

import django
from django.test.runner import DiscoverRunner

os.environ['DJANGO_SETTINGS_MODULE'] = 'mecc.settings.unittest'
django.setup()

test_runner = DiscoverRunner(pattern='test*.py', verbosity=2,
                             interactive=True, failfast=False)

failures = test_runner.run_tests(['mecc'])
sys.exit(failures)
