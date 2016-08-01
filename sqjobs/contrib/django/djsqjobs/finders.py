from sqjobs.utils import get_jobs_from_module

import logging
logger = logging.getLogger('sqjobs.contrib.django.utils')


def get_apps_names():
    """
    copied from django-extensions compatibility sheam
    """
    try:
        # django >= 1.7, to support AppConfig
        from django.apps import apps
        return [app.name for app in apps.get_app_configs()]
    except ImportError:
        from django.db import models
        return [app.__name__[:-7] for app in models.get_apps()]


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

    for app_name in get_apps_names():
        try:
            module = app_name + '.jobs'
            jobs.extend(get_jobs_from_module(module))
        except ImportError:
            pass

    return jobs
