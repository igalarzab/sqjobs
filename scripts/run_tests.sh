#! /bin/bash

set -e

py.test --cov .
python -m sqjobs.tests.django_test
