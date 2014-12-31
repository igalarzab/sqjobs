import inspect
import importlib

from django.db.models.loading import get_apps
from sqjobs import Job

import logging
logger = logging.getLogger('sqjobs.contrib.django')


def register_all_jobs(worker):
    jobs = get_all_jobs()

    for job in jobs:
        worker.register_job(job)

    try:
        jobs.remove(Job)
    except ValueError:
        pass

    return jobs


def get_all_jobs():
    jobs = []

    for app in get_apps():
        try:
            module = importlib.import_module(app.__name__[:-6] + 'jobs')
            jobs.extend(get_jobs_from_module(module))
        except ImportError:
            pass

    return jobs


def get_jobs_from_module(module):
    jobs = []

    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Job) and not inspect.isabstract(obj):
            logger.info('Found new job: %s', name)
            jobs.append(obj)

    return jobs
