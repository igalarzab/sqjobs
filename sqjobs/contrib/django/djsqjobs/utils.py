import importlib

from sqjobs.utils import get_jobs_from_module

import logging
logger = logging.getLogger('sqjobs.contrib.django.utils')


def get_apps():
    """
    copied from django-extensions compatibility sheam
    """
    try:
        # django >= 1.7, to support AppConfig
        from django.apps import apps
        return [app.models_module for app in apps.get_app_configs() if app.models_module]
    except ImportError:
        from django.db import models
        return models.get_apps()


def register_all_jobs(worker):
    """
    Register all the jobs in a worker
    """
    jobs = get_all_jobs()

    for job in jobs:
        worker.register_job(job)

    return jobs


def get_all_jobs():
    """
    Get all the jobs of the django INSTALLED_APPS
    """
    jobs = []

    for app in get_apps():
        try:
            module = app.__name__[:-6] + 'jobs'
            jobs.extend(get_jobs_from_module(module))
        except ImportError:
            pass

    return jobs
