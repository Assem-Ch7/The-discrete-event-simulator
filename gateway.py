# gateway.py
import random
from queue import Queue
from server import Server
from message import Message
from event import Event, EventType

class Gateway:
    """
    Coordinates message flow between Queue and Server(s).
    Handles arrivals, server allocation, service completion, and drops.
    """
    def __init__(self, mu, num_servers=1, queue_capacity=float('inf')):
        self._queue = Queue(max_size=queue_capacity)
        self._servers = [Server(mu) for _ in range(num_servers)]
        self._dropped_count = 0
        print(f"[LOG] Gateway initialized | Servers: {num_servers} | Queue Cap: {queue_capacity}")

    def _get_available_server(self):
        """Return first idle server, or None if all busy."""
        for srv in self._servers:
            if not srv.is_busy():
                return srv
        return None

    def handle_arrival(self, message: Message, scheduler=None) -> bool:
        """
        Process a RECV_MSG event.
        Returns True if message is accepted, False if dropped.
        If scheduler is provided, schedules DEPT_MSG when service starts.
        """
        if not self._queue.enqueue(message):
            self._dropped_count += 1
            print(f"[LOG] DROP | MsgID: {message.get_message_id()} | Dropped total: {self._dropped_count}")
            return False

        print(f"[LOG] ARRIVAL | MsgID: {message.get_message_id()} queued successfully.")

        # Try to start service immediately
        server = self._get_available_server()
        if server:
            self._start_service(message, server, scheduler)
        else:
            print("[LOG] ALL SERVERS BUSY | Message waiting in queue.")
        return True

    def handle_departure(self, finished_message: Message, scheduler=None):
        """
        Process a DEPT_MSG event.
        Frees the server and immediately serves next queued message if available.
        """
        # Find which server was busy with this message (simple match by reference)
        for srv in self._servers:
            if not srv.is_busy() and srv._current_message == finished_message:
                srv.end_service()
                print(f"[LOG] DEPARTURE | MsgID: {finished_message.get_message_id()} left Server {srv.get_server_id()}")
                break

        # Check queue for next message
        next_msg = self._queue.dequeue()
        if next_msg:
            server = self._get_available_server()
            if server:
                self._start_service(next_msg, server, scheduler)
        else:
            print("[LOG] QUEUE EMPTY | Server idle after departure.")

    def _start_service(self, message: Message, server: Server, scheduler=None):
        """Assign message to server, calculate service time, schedule DEPT_MSG."""
        service_time = server.get_service_time()
        server.start_service(message)
        dept_time = message.get_timestamp() + service_time  # or use scheduler.get_current_time()
        
        dept_event = Event(event_type=EventType.DEPT_MSG, event_time=dept_time, message=message)
        print(f"[LOG] SERVICE STARTED | MsgID: {message.get_message_id()} on Server {server.get_server_id()} | Dept @ {dept_time:.3f}")

        if scheduler:
            scheduler.add_event(dept_event)

    def get_dropped_count(self):
        return self._dropped_count

    def print_gateway_state(self):
        print(f"\n{'='*30} GATEWAY STATE {'='*30}")
        print(f"Dropped Messages: {self._dropped_count}")
        self._queue.print_queue()
        for srv in self._servers:
            srv.print_server()
        print("="*71 + "\n")
