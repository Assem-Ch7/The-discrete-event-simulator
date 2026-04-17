# message.py

class Message:
    def __init__(self, message_id, source, destination, timestamp):
        self._message_id = message_id
        self._source = source
        self._destination = destination
        self._timestamp = timestamp

    def get_message_id(self):
        return self._message_id
        
    def get_source(self):
        return self._source
        
    def get_destination(self):
        return self._destination
        
    def get_timestamp(self):
        return self._timestamp

    def set_timestamp(self, timestamp):
        self._timestamp = timestamp

    def print_message(self):
        print(f"Message ID: {self._message_id} | Source: {self._source} | "
              f"Dest: {self._destination} | Time: {self._timestamp}")