#! /bin/bash

set -e

py.test --verbose --cov --cov-report=html .
