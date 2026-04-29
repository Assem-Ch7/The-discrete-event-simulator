# event.py
from enum import Enum
from message import Message

class EventType(Enum):
    SEND_MSG = "SEND"
    RECV_MSG = "RECV"
    MSG_DEPT = "DEPT"

class Event:
    _id_counter = 101 

    def __init__(self, event_type, event_time, message=None):
        self._event_id = Event._id_counter
        Event._id_counter += 1
        
        self._event_type = event_type
        self._event_time = event_time
        self._message = message

    def get_event_id(self):
        return self._event_id

    def get_event_time(self):
        return self._event_time

    def get_event_type(self):
        return self._event_type

    def get_message(self):
        return self._message
    
    def set_event_time(self, event_time):
        self._event_time = event_time

    def set_event_type(self, event_type):
        self._event_type = event_type

    def __lt__(self, other):
        return self._event_time < other.get_event_time()

    def print_event(self):
        msg_id = self._message.get_message_id() if self._message else "None"
        print(f"Event ID: {self._event_id} | Type: {self._event_type.value} | "
              f"Time: {self._event_time} | MsgID: {msg_id}")