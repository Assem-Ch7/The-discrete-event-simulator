import random

class Client:
    _id_counter = 1

    def __init__(self, lambda_rate):
        self._client_id = Client._id_counter
        Client._id_counter += 1
        self._lambda = lambda_rate

    def get_next_interarrival_time(self):
        return random.expovariate(self._lambda)

    def get_client_id(self):
        return self._client_id

    def print_client(self):
        print(f"Client ID: {self._client_id} | Lambda: {self._lambda} msgs/sec")