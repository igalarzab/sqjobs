def create_raven_client(dsn):
    from raven import Client
    return Client(dsn)


def register_sentry(raven_client, worker):
    """
    Register sentry to send worker exceptions to it
    """

    def send_exception_to_sentry(job, *exc_info):
        raven_client.captureException(exc_info=exc_info, extra={
	    'job_id': job.id,
            'job_name': job.name,
            'retries': job.retries,
	})

    # TODO: Not yet...
    #  worker.add_exception_handler(send_exception_to_sentry)
