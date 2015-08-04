# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('job_id', models.TextField(unique=True, verbose_name=b'job id')),
                ('job_name', models.CharField(max_length=255, verbose_name=b'job name')),
                ('status', models.CharField(default=b'PENDING', max_length=7, verbose_name=b'job status', choices=[(b'PENDING', b'PENDING'), (b'SUCCESS', b'SUCCESS'), (b'TIMEOUT', b'TIMEOUT'), (b'FAILURE', b'FAILURE')])),
                ('result', models.TextField(default=None, null=True)),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name=b'started at')),
                ('date_done', models.DateTimeField(null=True, verbose_name=b'done at')),
                ('traceback', models.TextField(null=True, verbose_name=b'traceback', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'name')),
                ('task', models.CharField(max_length=255, verbose_name=b'task')),
                ('args', models.TextField(default=None, null=True, verbose_name=b'args')),
                ('kwargs', models.TextField(default=None, null=True, verbose_name=b'kwargs')),
                ('schedule', models.CharField(max_length=255, verbose_name=b'schedule')),
                ('timezone', models.CharField(default=b'UTC', max_length=63, verbose_name=b'timezone')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name=b'created on')),
                ('next_execution', models.DateTimeField(verbose_name=b'next execution on')),
                ('enabled', models.BooleanField(default=True, verbose_name=b'enabled')),
                ('skip_delayed_jobs_next_time', models.BooleanField(default=True, verbose_name=b'skip jobs if delayed')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
