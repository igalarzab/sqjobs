SQJobs v\ |version| documentation
=================================

SQJobs (simple queue jobs) is a Python library for queueing jobs and processing them using
background workers and `SQS <https://aws.amazon.com/sqs/>`_ as the broker.

Some of it features are:

* It follows a `KISS <https://en.wikipedia.org/wiki/KISS_principle>`_ principle, it does one thing
  and only one thing: execute jobs.
* The source code is really simple and easy to debug.
* Jobs execution is fast (there are no boilerplate around the jobs).
* It can scale horizontally (workers don't store any state inside the machines).
* New brokers can be created (now it only supports `SQS <https://aws.amazon.com/sqs/>`_ from Amazon).

Ready to get started? Check out the :ref:`installation guide <installing>`.


Source code
-----------

You can access the source code at `Github <https://github.com/igalarzab/sqjobs>`_.


Contents
--------

.. toctree::
   :maxdepth: 2

   chapters/installing
   chapters/quickstart
   chapters/advanced
   chapters/faq
   chapters/changelog
