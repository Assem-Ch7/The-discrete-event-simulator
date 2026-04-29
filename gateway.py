import random
from queue import Queue
from server import Server
from message import Message
from event import Event, EventType

class Gateway:
    def __init__(self, mu, num_servers=1, queue_capacity=float('inf')):
        self._queue = Queue(max_size=queue_capacity)
        self._servers = [Server(mu) for _ in range(num_servers)]
        self._dropped_count = 0
        print(f"[LOG] Gateway initialized | Servers: {num_servers} | Queue Cap: {queue_capacity}")

    def _get_available_server(self):
        for srv in self._servers:
            if not srv.is_busy():
                return srv
        return None
 
    def handle_arrival(self, message: Message, scheduler) -> bool:
        server = self._get_available_server()
        if server:
            print(f"[LOG] ARRIVAL | MsgID: {message.get_message_id()} bypasses queue directly to Server.")
            self._start_service(message, server, scheduler)
            return True
            
        # 2. If servers are busy, THEN try to put it in the queue
        if not self._queue.enqueue(message):
            self._dropped_count += 1
            print(f"[LOG] DROP | MsgID: {message.get_message_id()} | Dropped total: {self._dropped_count}")
            return False

        print(f"[LOG] ARRIVAL | MsgID: {message.get_message_id()} queued successfully.")
        return True

    def handle_departure(self, finished_message: Message, scheduler):
        for srv in self._servers:
            if srv.is_busy() and srv._current_message == finished_message:
                srv.end_service()
                print(f"[LOG] DEPARTURE | MsgID: {finished_message.get_message_id()} left Server {srv.get_server_id()}")
                break

        next_msg = self._queue.dequeue()
        if next_msg:
            server = self._get_available_server()
            if server:
                self._start_service(next_msg, server, scheduler)
        else:
            print("[LOG] QUEUE EMPTY | Server idle after departure.")

    def _start_service(self, message: Message, server: Server, scheduler):
        service_time = server.get_service_time()
        server.start_service(message)
        
        # CRITICAL FIX: Service ends at the current simulation time + the duration of the service
        current_time = scheduler.get_current_time()
        dept_time = current_time + service_time  
        
        dept_event = Event(event_type=EventType.MSG_DEPT, event_time=dept_time, message=message)
        print(f"[LOG] SERVICE STARTED | MsgID: {message.get_message_id()} on Server {server.get_server_id()} | Dept @ {dept_time:.3f}")

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