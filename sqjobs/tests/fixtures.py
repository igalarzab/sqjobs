from ..job import Job


class Adder(Job):
    name = 'adder'
    queue = 'default'
    retry_time = 10

    def run(self, num1, num2):
        return num1 + num2


class FakeAdder(Adder):
    retry_time = None


class AbstractAdder(Adder):
    abstract = True


class ComplexRetryJob(Adder):
    name = 'complex'
    retry_time = 10

    def next_retry(self):
        return (self.retries + 1) * self.retry_time
