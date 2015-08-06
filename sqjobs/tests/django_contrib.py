#!/usr/bin/env python
import os
import sys

from django.conf import settings
import django


DEFAULT_SETTINGS = {
    'INSTALLED_APPS': (
        'sqjobs',
        'sqjobs.tests',
        'sqjobs.contrib.django.djsqjobs'
    ),
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    'USE_TZ': 'true',
    'SILENCED_SYSTEM_CHECKS': ["1_7.W001"],
}

if not settings.configured:
    settings.configure(**DEFAULT_SETTINGS)

if hasattr(django, 'setup'):
    django.setup()

parent = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))

sys.path.insert(0, parent)


from django.test.runner import DiscoverRunner

res = DiscoverRunner(failfast=False).run_tests([
    'sqjobs.tests'
], verbosity=1)

sys.exit(res)
