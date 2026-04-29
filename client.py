import random
from message import Message

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

    def generate_message(self, current_time, destination=0):
        arrival_time = current_time + self.get_next_interarrival_time()
        return Message(source=self._client_id, destination=destination, timestamp=arrival_time)

    def print_client(self):
        print(f"Client ID: {self._client_id} | Lambda: {self._lambda} msgs/sec")