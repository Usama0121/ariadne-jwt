#!/usr/bin/env python

import os
import sys

import django

from django.conf import settings
from django.test.runner import DiscoverRunner

DEFAULT_SETTINGS = dict(
    INSTALLED_APPS=[
        'django.contrib.auth',
        'django.contrib.contenttypes'
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test'
        }
    },
    SECRET_KEY='secret',
    AUTHENTICATION_BACKENDS=[
        'ariadne_jwt.backends.JWTBackend'
    ],
    ROOT_URLCONF='tests.urls'
)


def run_tests():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    failures = DiscoverRunner(verbosity=1, interactive=True, failfast=False).run_tests(['tests'])

    sys.exit(failures)


if __name__ == '__main__':
    run_tests()
