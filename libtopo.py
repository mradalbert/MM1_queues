import numpy as numpy


class Event():
    def __init__(self, time):
        self.time = time


class Queue():
    def __init__(self, lam, mi):
        self.lam = lam
        self.mi = mi
        self.ro = lam / mi
        self.current_queue_time = 0
        self.server_ready = 1
        self.next_request_time = self.generate_request_time(0)
        self.next_service_time = self.generate_service_time(0)
        self.requests = list()
        self.results = list()

    def generate_service_time(self, input):
        return input + numpy.random.exponential(1 / self.mi, 1)

    def generate_request_time(self, input):
        return input + numpy.random.exponential(1 / self.lam, 1)

    def execute_request(self):
        if self.server_ready:
            self.server_ready = 0
            self.results.append(0.0)
        else:
            self.requests.append(Event(self.current_queue_time))

        self.current_queue_time = self.next_request_time
        self.next_request_time = self.generate_request_time(self.next_request_time)

    def execute_service(self):
        if not self.server_ready:
            if len(self.requests) > 0:
                self.results.append(self.current_queue_time - self.requests.pop(0).time)
            else:
                self.server_ready = 1

        self.current_queue_time = self.next_service_time
        self.next_service_time = self.generate_service_time(self.next_service_time)

    def make_step(self):
        if self.next_service_time < self.next_request_time:
            self.execute_service()
        else:
            self.execute_request()

    def make_step_server_dead(self):
        self.execute_request()