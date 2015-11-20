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
    def run(self, num1, num2):
        return num1 + num2
```

## Sample Job

```python
from sqjobs.job import Job

class AdderJob(Job):
    name = 'adder_job'
    queue = 'my_queue'

    def run(self, *args, **kwargs):
        return sum(args)
```

# Launching a Job

```python
from sqjobs import create_sqs_broker
from myapp.jobs import AdderJob

kwargs = {
    'access_key': settings.SQJOBS_SQS_ACCESS_KEY,
    'secret_key': settings.SQJOBS_SQS_ACCESS_KEY
}
broker = create_sqs_broker(**kwargs)
broker.add_job(AdderJob, *[1, 2, 3, 4])
```

# Eager mode

Eager mode is a simpler execution mode. Tasks are run synchronously by the broker itself so there is no need for a queue nor running workers. It's meant for development and unit testing.

```python
>>> from sqjobs import create_eager_broker
>>> broker = create_eager_broker()
>>> from jobs import AdderJob
>>> job_added = broker.add_job(AdderJob, *[1, 2, 3])
>>> job_added 
('fdb005d3-276f-4f75-8e8e-c8fcde67043c', AdderJob())
>>> job_added[1].result
6
```
