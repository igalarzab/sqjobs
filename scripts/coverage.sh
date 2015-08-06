#! /bin/bash

set -e

py.test --cov . --cov-report=html
