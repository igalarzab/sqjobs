from django.test import TestCase
from django.core.management import call_command
from sqjobs.brokers.standard import Standard
from sqjobs.brokers.eager import Eager
from sqjobs.contrib.django.djsqjobs.models import PeriodicJob
from sqjobs.contrib.django.djsqjobs.models import JobStatus


from ...fixtures import Adder, Divider
from .django_fixtures import ResultDivider

from datetime import datetime
import pytz

from mock.mock import patch


class DjangoTestCase(TestCase):
    fixtures = ['sqjobs/tests/djsqjobs_tests-fixture.json']

    def setUp(self):
        call_command('loaddata', self.fixtures[0], verbosity=0)


class ResultJobsTests(DjangoTestCase):

    def test_result_jobs(self):
        result_divider = ResultDivider()
        result_divider.id = '1234'
        self.assertFalse(result_divider.properly_setup)
        result_divider.pre_run()
        self.assertEqual(repr(result_divider.job_status),
            '<JobStatus (ResultDivider()): 1234 status->PENDING>'
        )
        self.assertEqual(
            result_divider.job_status.to_dict(),
            {
                'status': 'PENDING',
                'job_id': '1234',
                'date_done': None,
                'traceback': None,
                'result': None,
                'date_started': None,
                'job_name': 'ResultDivider()'
            }
        )
        self.assertTrue(result_divider.properly_setup)
        self.assertEqual(result_divider.job_status.status, JobStatus.PENDING)
        result_divider.run(3, 1)
        self.assertTrue(result_divider.properly_setup)
        result_divider.on_success()
        self.assertEqual(result_divider.job_status.status, JobStatus.SUCCESS)
        result_divider.on_failure()
        self.assertEqual(result_divider.job_status.status, JobStatus.FAILURE)
        self.assertEqual(result_divider.err, 'ZeroDivisionError')
        result_divider.post_run()
        self.assertLessEqual(result_divider.job_status.date_done, datetime.now())
        self.assertEqual(result_divider.job_status.result, '3')
