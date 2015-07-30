from django.test import TestCase
from ..brokers.broker import Standard
from ..brokers.eager import Eager
from sqjobs.contrib.django.djsqjobs.beat import Beat
from sqjobs.contrib.django.djsqjobs.models import PeriodicJob
from sqjobs.contrib.django.djsqjobs.models import JobStatus

from .fixtures import Adder, Divider
from .django_fixtures import ResultDivider
from ..connectors.dummy import Dummy

from datetime import datetime
import pytz

from mock.mock import patch


class DjangoTestCase(TestCase):
    fixtures = ['sqjobs/tests/djsqjobs_tests-fixture.json']

    def setUp(self):
        from django.core.management.commands.loaddata import Command

        loaddata_command = Command()
        loaddata_command.using = 'default'
        loaddata_command.ignore = None
        loaddata_command.app_label = None
        loaddata_command.verbosity = 0
        loaddata_command.hide_empty = None
        loaddata_command.loaddata(self.fixtures)


class PeriodicJobsTests(DjangoTestCase):
    beat = Beat(None, 10, True)
    beat.register_job(Adder)

    def test_get_expired_jobs(self):
        assert len(self.beat.get_expired_jobs()) == 2

    def test_add_delayed_job_info_and_programmed_date(self):
        expired_job = PeriodicJob.objects.get(pk=2)
        expired_job_kwargs = self.beat.get_job_kwargs(expired_job)
        kwargs_with_delayed_info = self.beat.add_delayed_job_info(
            expired_job, expired_job_kwargs
        )
        assert kwargs_with_delayed_info['num1'] == 1
        assert kwargs_with_delayed_info['num2'] == 2
        assert kwargs_with_delayed_info[PeriodicJob.PROGRAMMED_DATE] == expired_job.next_execution.astimezone(pytz.timezone(expired_job.timezone)).isoformat()
        assert kwargs_with_delayed_info[PeriodicJob.DELAYED_JOB]

    def test_add_programmed_date_but_not_delayed_job_info(self):
        future_job = PeriodicJob.objects.get(pk=4)
        future_job_kwargs = self.beat.get_job_kwargs(future_job)
        kwargs_without_delayed_info = self.beat.add_delayed_job_info(
            future_job, future_job_kwargs
        )
        assert kwargs_without_delayed_info['num1'] == 2
        assert kwargs_without_delayed_info['num2'] == 1
        assert kwargs_without_delayed_info[PeriodicJob.PROGRAMMED_DATE] == future_job.next_execution.astimezone(pytz.timezone(future_job.timezone)).isoformat()
        assert PeriodicJob.DELAYED_JOB not in kwargs_without_delayed_info

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
            assert future_next_execution > datetime.now(pytz.timezone('UTC'))

            beat.enqueue_next_jobs(beat.get_expired_jobs())

            expired_job = PeriodicJob.objects.get(pk=2)
            assert expired_minute == expired_job.next_execution.minute
            assert expired_second == expired_job.next_execution.second
            assert expired_job.next_execution > expired_next_execution
            assert expired_job.next_execution > datetime.now(pytz.timezone('UTC'))

            future_job = PeriodicJob.objects.get(pk=4)
            assert future_job.next_execution == future_next_execution
            assert future_job.next_execution > datetime.now(pytz.timezone('UTC'))

        assert mock_add_job.called

    def test_enqueue_jobs_dont_skip(self):
        broker = Standard(None)
        with patch.object(Standard, 'add_job') as mock_add_job:
            beat = Beat(broker, 10, False)
            beat.register_job(Adder)
            beat.register_job(Divider)

            expired_job = PeriodicJob.objects.get(pk=2)
            expired_next_execution = expired_job.next_execution
            expired_minute = expired_next_execution.minute
            expired_second = expired_next_execution.second

            future_job = PeriodicJob.objects.get(pk=4)
            future_next_execution = future_job.next_execution
            assert future_next_execution > datetime.now(pytz.timezone('UTC'))

            beat.enqueue_next_jobs(beat.get_expired_jobs())

            expired_job = PeriodicJob.objects.get(pk=2)
            assert expired_minute == expired_job.next_execution.minute
            assert expired_second == expired_job.next_execution.second
            assert expired_job.next_execution > expired_next_execution
            assert expired_job.next_execution < datetime.now(pytz.timezone('UTC'))

            future_job = PeriodicJob.objects.get(pk=4)
            assert future_job.next_execution == future_next_execution
            assert future_job.next_execution > datetime.now(pytz.timezone('UTC'))

        assert mock_add_job.called

    def test_zero_periodic_tasks_enabled(self):
        for i in (2, 3, 4):
            expired_job = PeriodicJob.objects.get(pk=i)
            expired_job.enabled = False
            expired_job.save()

        assert not self.beat.get_expired_jobs()

    def test_no_periodic_tasks_at_all(self):
        for i in (2, 3, 4):
            expired_job = PeriodicJob.objects.get(pk=i)
            expired_job.delete()

        assert not self.beat.get_expired_jobs()

    def test_create_periodic_job(self):
        my_periodic_job = PeriodicJob(schedule="2 15 * * *", timezone="Europe/Madrid")
        my_periodic_job.save()
        assert my_periodic_job.next_execution.minute == 2
        assert my_periodic_job.next_execution > datetime.now(pytz.timezone('UTC'))


class ResultJobsTests(DjangoTestCase):

    def test_result_jobs(self):
        result_divider = ResultDivider()
        result_divider.id = '1234'
        assert not result_divider.properly_setup
        result_divider.set_up()
        assert repr(result_divider.job_status) == '<JobStatus: <Job (ResultDivider()): 1234 state->PENDING>>'
        assert result_divider.job_status.to_dict() == {
            'status': u'PENDING',
            'job_id': '1234',
            'date_done': None,
            'traceback': None,
            'result': None,
            'date_started': None,
            'job_name': 'ResultDivider()'
        }
        assert result_divider.properly_setup
        assert result_divider.job_status.status == JobStatus.PENDING
        result_divider.run(3, 1)
        assert result_divider.properly_setup
        result_divider.on_success()
        assert result_divider.job_status.status == JobStatus.SUCCESS
        result_divider.on_failure()
        assert result_divider.job_status.status == JobStatus.FAILURE
        assert result_divider.err == 'ZeroDivisionError'
        result_divider.tear_down()
        assert result_divider.job_status.date_done <= datetime.now()
        assert result_divider.job_status.result == '3'
