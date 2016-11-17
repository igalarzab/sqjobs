.. _changelog:

Changelog
=========

v0.7.1
------

* Added the possibility of queueing tasks using the task name.


v0.7.0
------

* Added :ref:`new helpers <advanced>` to use SQJobs with Django.
* Fixed a bug that forces the inmediate retry of a job when it fails.
* Fixed an exception when running a job with a overwrited default queue name.
* Improved the documentation.

v0.6.7
------

* Adding the current working directory to the python path when using the CLI.

v0.6.6
------

* Fix how job names are calculated when a custom one is not specified.

v0.6.5
------

* Now you can change the visibility time of an specific job, overwriting the queue's one.


v0.6.1
------

* Documentation created.
