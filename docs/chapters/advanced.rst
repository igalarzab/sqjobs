.. _advanced:

Advanced topics
===============

This page explains some advanced topics of SQJobs. First, make sure that SQJobs
is :ref:`installed <installing>` and is in it lastest version.

Using sqjobs with django
------------------------

SQJobs provides some helpers to be used with Django. To be able to used them you will need first to
edit your settings and install the SQJobs's django app::

    INSTALLED_APPS += ("sqjobs.contrib.django.djsqjobs", )

Then, you'll have to configure your connection to SQS with the following settings::

    SQJOBS_SQS_ACCESS_KEY = '????'
    SQJOBS_SQS_SECRET_KEY = '????'
    SQJOBS_SQS_REGION_NAME = 'eu-west-1'

From now on your manage.py script will have a new command to execute the SQJobs worker::

    $ ./manage.py worker QUEUE_NAME

By default, it will search for all the ``jobs`` modules (ex: a ``jobs.py`` file near your
``models.py``) in your ``INSTALLED_APPS`` settings and it will load all the jobs contained in them.

Also, you can send new jobs to SQS using the ``add_job`` method::

    from sqjobs.contrib.django.djsqjobs import add_job
    from .jobs import Adder

    def my_view(request):
        add_job(Adder, 3, 4)


Sending errors to sentry
------------------------


Storing job results in a database
---------------------------------


Eager mode
----------
