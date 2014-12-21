from ..job import Job


class Adder(Job):
    name = 'adder'
    queue = 'default'
    retry_time = 10

    def run(self, num1, num2):
        return num1 + num2


class ComplexRetryJob(Job):
    name = 'complex'
    retry_time = 10

    def run(self, counter):
        counter += 1
        return counter

    def next_retry(self):
        return (self.retries + 1 ) * self.retry_time
