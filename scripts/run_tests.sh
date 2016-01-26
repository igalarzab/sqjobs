#! /bin/bash

set -e

py.test --verbose --cov .
python -m sqjobs.tests.contrib.django.django_contrib
