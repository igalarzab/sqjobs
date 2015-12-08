# sqjobs

[![Build Status](https://travis-ci.org/igalarzab/sqjobs.svg?branch=master)](https://secure.travis-ci.org/igalarzab/sqjobs)
[![Coverage Status](https://coveralls.io/repos/igalarzab/sqjobs/badge.png?branch=master)](https://coveralls.io/r/igalarzab/sqjobs?branch=master)
[![Code Health](https://landscape.io/github/igalarzab/sqjobs/master/landscape.svg)](https://landscape.io/github/igalarzab/sqjobs/master)


## Installation

Simply use pip to install the last version of ``sqjobs``

    pip install sqjobs


## Getting started

First you have to create jobs. A job is simply a class that inherits from ``Job``.

```python
from sqjobs import Job

class Adder(Job):
    queue = 'queue_name'

    def run(self, num1, num2):
        return num1 + num2
```

Then, you can launch the job creating a new broker.

```python
from sqjobs import create_sqs_broker

config = {
    'access_key': settings.SQJOBS_SQS_ACCESS_KEY,
    'secret_key': settings.SQJOBS_SQS_ACCESS_KEY
}

broker = create_sqs_broker(**config)
broker.add_job(AdderJob, 1, 2, queue_name='other_queue_name')
```
