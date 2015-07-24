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
                ('job_id', models.CharField(unique=True, max_length=255, verbose_name='job id')),
                ('job_type', models.CharField(max_length=255, verbose_name='job type')),
                ('status', models.CharField(default=b'PENDING', max_length=7, verbose_name='job status', choices=[(b'PENDING', b'PENDING'), (b'SUCCESS', b'SUCCESS'), (b'TIMEOUT', b'TIMEOUT'), (b'FAILURE', b'FAILURE')])),
                ('result', models.TextField(default=None, null=True)),
                ('date_started', models.DateTimeField(auto_now_add=True, verbose_name='started at')),
                ('date_done', models.DateTimeField(null=True, verbose_name='done at')),
                ('traceback', models.TextField(null=True, verbose_name='traceback', blank=True)),
            ],
            options={
                'db_table': 'sqjobs_jobstatus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PeriodicJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('task', models.CharField(max_length=255, verbose_name='task')),
                ('args', models.TextField(default=None, null=True, verbose_name='args')),
                ('schedule', models.CharField(max_length=255, verbose_name='schedule')),
                ('timezone', models.CharField(default=b'UTC', max_length=63, verbose_name='timezone')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('next_execution', models.DateTimeField(verbose_name='next execution on')),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled'))
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
