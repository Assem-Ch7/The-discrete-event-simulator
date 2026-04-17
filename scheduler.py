import heapq
from event import Event

class Scheduler:
    def __init__(self):
        self._events = []
        self._current_time = 0.0

    def add_event(self, event):
        heapq.heappush(self._events, event)

    def get_event(self):
        if self._events:
            next_event = heapq.heappop(self._events)
            self._current_time = next_event.get_event_time()
            return next_event
        return None

    def get_current_time(self):
        return self._current_time