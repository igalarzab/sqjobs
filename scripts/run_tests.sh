#! /bin/bash

py.test --cov .
python -m sqjobs.tests.django_test
