from django.test import TestCase
from django.core.management import call_command
from ..brokers.broker import Standard
from ..brokers.eager import Eager
from sqjobs.contrib.django.djsqjobs.beat import Beat
from sqjobs.contrib.django.djsqjobs.models import PeriodicJob
from sqjobs.contrib.django.djsqjobs.models import JobStatus


from .fixtures import Adder, Divider
from .django_fixtures import ResultDivider

from datetime import datetime
import pytz

from mock.mock import patch


class DjangoTestCase(TestCase):
    fixtures = ['sqjobs/tests/djsqjobs_tests-fixture.json']

    def setUp(self):
        call_command('loaddata', self.fixtures[0], verbosity=0)

        self.beat = Beat(None, 10, True)
        self.beat.register_job(Adder)


class PeriodicJobsTests(DjangoTestCase):
    def test_get_expired_jobs(self):
        self.assertEqual(len(self.beat.get_expired_jobs()), 2)

    def test_add_delayed_job_info_and_programmed_date(self):
        expired_job = PeriodicJob.objects.get(pk=2)
        expired_job_kwargs = self.beat.get_job_kwargs(expired_job)
        kwargs_with_delayed_info = self.beat.add_delayed_job_info(
            expired_job, expired_job_kwargs
        )
        self.assertEqual(kwargs_with_delayed_info['num1'], 1)
        self.assertEqual(kwargs_with_delayed_info['num2'], 2)
        self.assertEqual(
            kwargs_with_delayed_info[PeriodicJob.PROGRAMMED_DATE],
            expired_job.next_execution.astimezone(
                pytz.timezone(expired_job.timezone)
            ).isoformat()
        )
        self.assertTrue(kwargs_with_delayed_info[PeriodicJob.DELAYED_JOB])

    def test_add_programmed_date_but_not_delayed_job_info(self):
        future_job = PeriodicJob.objects.get(pk=4)
        future_job_kwargs = self.beat.get_job_kwargs(future_job)
        kwargs_without_delayed_info = self.beat.add_delayed_job_info(
            future_job, future_job_kwargs
        )
        self.assertEqual(kwargs_without_delayed_info['num1'], 2)
        self.assertEqual(kwargs_without_delayed_info['num2'], 1)
        self.assertEqual(
            kwargs_without_delayed_info[PeriodicJob.PROGRAMMED_DATE],
            future_job.next_execution.astimezone(
                pytz.timezone(future_job.timezone)
            ).isoformat()
        )
        self.assertNotIn(PeriodicJob.DELAYED_JOB, kwargs_without_delayed_info)

    def test_enqueue_jobs(self):
        broker = Standard(None)
        with patch.object(Standard, 'add_job') as mock_add_job:

            beat = Beat(broker, 10, True)
            beat.register_job(Adder)
            beat.register_job(Divider)

            expired_job = PeriodicJob.objects.get(pk=2)
            expired_next_execution = expired_job.next_execution
            expired_minute = expired_next_execution.minute
            expired_second = expired_next_execution.second

            future_job = PeriodicJob.objects.get(pk=4)
            future_next_execution = future_job.next_execution
            self.assertGreater(future_next_execution, datetime.now(pytz.timezone('UTC')))

            beat.enqueue_next_jobs(beat.get_expired_jobs())

            expired_job = PeriodicJob.objects.get(pk=2)
            self.assertEqual(expired_minute, expired_job.next_execution.minute)
            self.assertEqual(expired_second, expired_job.next_execution.second)
            self.assertGreater(
                expired_job.next_execution,
                expired_next_execution
            )
            self.assertGreater(
                expired_job.next_execution,
                datetime.now(pytz.timezone('UTC'))
            )

            future_job = PeriodicJob.objects.get(pk=4)
            self.assertEqual(future_job.next_execution, future_next_execution)
            self.assertGreater(
                future_job.next_execution,
                datetime.now(pytz.timezone('UTC'))
            )

        assert mock_add_job.called_with(num1=1, num2=2, sqjobs_programmed_date='2015-07-26T17:01:00+02:00')

    def test_enqueue_jobs_dont_skip(self):
        broker = Standard(None)
        with patch.object(Standard, 'add_job') as mock_add_job:
            beat = Beat(broker, 10, False)
            beat.register_job(Adder)
            beat.register_job(Divider)

            expired_job = PeriodicJob.objects.get(pk=2)
            expired_next_execution = expired_job.next_execution

            future_job = PeriodicJob.objects.get(pk=4)
            future_next_execution = future_job.next_execution
            self.assertGreater(
                future_next_execution,
                datetime.now(pytz.timezone('UTC'))
            )

            beat.enqueue_next_jobs(beat.get_expired_jobs())

            expired_job = PeriodicJob.objects.get(pk=2)
            self.assertEqual(
                expired_job.next_execution.isoformat(),
                "2015-07-26T16:01:00+00:00"
            )

            future_job = PeriodicJob.objects.get(pk=4)
            self.assertEqual(
                future_job.next_execution,
                future_next_execution
            )
            self.assertGreater(
                future_job.next_execution,
                datetime.now(pytz.timezone('UTC'))
            )

        assert mock_add_job.called_with(num1=1, num2=2, sqjobs_programmed_date='2015-07-26T17:01:00+02:00')

    def test_zero_periodic_tasks_enabled(self):
        for i in (2, 3, 4):
            expired_job = PeriodicJob.objects.get(pk=i)
            expired_job.enabled = False
            expired_job.save()

        self.assertEqual(len(self.beat.get_expired_jobs()), 0)

    def test_no_periodic_tasks_at_all(self):
        for i in (2, 3, 4):
            expired_job = PeriodicJob.objects.get(pk=i)
            expired_job.delete()

        self.assertEqual(len(self.beat.get_expired_jobs()), 0)

    def test_create_periodic_job(self):
        my_periodic_job = PeriodicJob(schedule="2 15 * * *", timezone="Europe/Madrid")
        my_periodic_job.save()
        self.assertGreaterEqual(my_periodic_job.next_execution, datetime.now(pytz.timezone('UTC')))
        self.assertEqual(my_periodic_job.next_execution.minute, 2)


class ResultJobsTests(DjangoTestCase):

    def test_result_jobs(self):
        result_divider = ResultDivider()
        result_divider.id = '1234'
        self.assertFalse(result_divider.properly_setup)
        result_divider.set_up()
        self.assertEqual(repr(result_divider.job_status),
            '<JobStatus: <Job (ResultDivider()): 1234 status->PENDING>>'
        )
        self.assertEqual(
            result_divider.job_status.to_dict(),
            {
                'status': u'PENDING',
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
        result_divider.tear_down()
        self.assertLessEqual(result_divider.job_status.date_done, datetime.now())
        self.assertEqual(result_divider.job_status.result, '3')
