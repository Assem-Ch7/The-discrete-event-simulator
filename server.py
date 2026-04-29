import random

class Server:
    _id_counter = 1

    def __init__(self, mu):
        self._server_id = Server._id_counter
        Server._id_counter += 1
        self._mu = mu
        self._busy = False
        self._current_message = None

    def get_service_time(self):
        return random.expovariate(self._mu)

    def get_server_id(self):
        return self._server_id

    def start_service(self, message):
        self._busy = True
        self._current_message = message

    def end_service(self):
        finished_message = self._current_message
        self._busy = False
        self._current_message = None
        return finished_message
    
    def is_busy(self):
        return self._busy

    def print_server(self):
        status  = "Busy" if self._busy else "Idle"
        print(f"Server ID: {self._server_id} | Mu: {self._mu} msgs/sec | Status: {status}")