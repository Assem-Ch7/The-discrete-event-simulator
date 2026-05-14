from queue import Queue
from server import Server
from message import Message
from event import Event, EventType


class Gateway:

    def __init__(self, mu, num_servers=1, queue_capacity=float('inf'), metrics=None):
        self._queue         = Queue(max_size=queue_capacity)
        self._servers       = [Server(mu) for _ in range(num_servers)]
        self._dropped_count = 0
        self._metrics       = metrics
        print(f"[LOG] Gateway initialized | Servers: {num_servers} | Queue Cap: {queue_capacity}")

    def _get_available_server(self):
        for srv in self._servers:
            if not srv.is_busy():
                return srv
        return None

    def _start_service(self, message: Message, server: Server, scheduler):
        service_time = server.get_service_time()
        server.start_service(message)

        current_time = scheduler.get_current_time()
        dept_time    = current_time + service_time

        dept_event = Event(event_type=EventType.MSG_DEPT,
                           event_time=dept_time, message=message)
        print(f"[LOG] SERVICE STARTED | MsgID: {message.get_message_id()} "
              f"on Server {server.get_server_id()} | Dept @ {dept_time:.3f}")

        scheduler.add_event(dept_event)

    def receive_msg(self, message: Message, scheduler) -> bool:
        server = self._get_available_server()
        if server:
            print(f"[LOG] ARRIVAL | MsgID: {message.get_message_id()} "
                  f"bypasses queue directly to Server.")
            self._start_service(message, server, scheduler)
            if self._metrics:
                self._metrics.record_arrival()
            return True

        if not self._queue.enqueue(message):
            self._dropped_count += 1
            print(f"[LOG] DROP | MsgID: {message.get_message_id()} "
                  f"| Dropped total: {self._dropped_count}")
            if self._metrics:
                self._metrics.record_drop()
            return False

        print(f"[LOG] ARRIVAL | MsgID: {message.get_message_id()} queued successfully.")
        if self._metrics:
            self._metrics.record_arrival()
        return True

    def departure_msg(self, finished_message: Message, scheduler):
        for srv in self._servers:
            if srv.is_busy() and srv._current_message is finished_message:
                srv.end_service()
                print(f"[LOG] DEPARTURE | MsgID: {finished_message.get_message_id()} "
                      f"left Server {srv.get_server_id()}")
                break

        next_msg = self._queue.dequeue()
        if next_msg:
            server = self._get_available_server()
            if server:
                self._start_service(next_msg, server, scheduler)
        else:
            print("[LOG] QUEUE EMPTY | Server idle after departure.")

    def get_dropped_count(self):
        return self._dropped_count

    def get_n_system(self):
        in_service = sum(1 for s in self._servers if s.is_busy())
        return self._queue.size() + in_service

    def get_n_queue(self):
        return self._queue.size()

    def set_metrics(self, metrics):
        self._metrics = metrics

    def print_gateway_state(self):
        print(f"\n{'='*30} GATEWAY STATE {'='*30}")
        print(f"Dropped Messages: {self._dropped_count}")
        self._queue.print_queue()
        for srv in self._servers:
            srv.print_server()
        print("=" * 71 + "\n")
