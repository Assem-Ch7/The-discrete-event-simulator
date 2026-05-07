from message import Message
from event import Event, EventType
from scheduler import Scheduler
from client import Client
from server import Server
from queue import Queue
from gateway import Gateway
from metrics import Metrics


class Main:

    @staticmethod
    def GenerateTrace(e):
        """Print one formatted trace line for an event."""
        e_time = e.get_event_time()
        e_type = e.get_event_type().value
        msg    = e.get_message()

        if e_type == "SEND":
            node = msg.get_source()
        elif e_type == "RECV":
            node = msg.get_destination()
        else:
            node = "0"

        print(f"{e_time:<9.3f} {node:<5} {e_type:<6} {msg.get_source():<6} {msg.get_destination():<5} {msg.get_message_id()}")

    @staticmethod
    def test_message():
        print("--- Testing Message ---")
        msg1 = Message(source=1, destination=0, timestamp=1.202)
        msg2 = Message(source=3, destination=0, timestamp=2.320)
        msg1.print_message()
        msg2.print_message()
        print()

    @staticmethod
    def test_event():
        print("--- Testing Event & Scheduler ---")

        msg1 = Message(source=1, destination=0, timestamp=1.202)
        msg2 = Message(source=3, destination=0, timestamp=2.320)

        event1 = Event(event_type=EventType.SEND_MSG, event_time=1.202, message=msg1)
        event2 = Event(event_type=EventType.RECV_MSG, event_time=1.916, message=msg1)
        event3 = Event(event_type=EventType.SEND_MSG, event_time=2.320, message=msg2)
        event4 = Event(event_type=EventType.RECV_MSG, event_time=2.391, message=msg2)
        event5 = Event(event_type=EventType.MSG_DEPT, event_time=4.572, message=msg1)
        event6 = Event(event_type=EventType.MSG_DEPT, event_time=5.916, message=msg2)

        scheduler = Scheduler()
        for ev in [event4, event1, event6, event2, event5, event3]:
            scheduler.add_event(ev)

        print(f"{'time':<9} {'node':<5} {'event':<6} {'source':<6} {'dest.':<5} {'msgID'}")
        while True:
            current_event = scheduler.get_event()
            if not current_event:
                break
            Main.GenerateTrace(current_event)
        print()

    @staticmethod
    def test_client():
        print("--- Testing Client ---")
        # Initialize client with lambda = 4 (from M/M/1 example)
        client = Client(lambda_rate=4)
        client.print_client()

        print("\nGenerating consecutive messages:")
        # current_time drives the absolute timestamp of each message
        msg1 = client.generate_message(current_time=0.0, destination=2)
        msg2 = client.generate_message(current_time=msg1.get_timestamp(), destination=3)

        msg1.print_message()
        msg2.print_message()

        samples = [round(client.get_next_interarrival_time(), 4) for _ in range(5)]
        print(f"  5 inter-arrival samples (lambda=4): {samples}")
        print()

    @staticmethod
    def test_queue():
        print("--- Testing Queue ---")
        q = Queue(max_size=2)

        msg1 = Message(source=1, destination=0, timestamp=1.0)
        msg2 = Message(source=2, destination=0, timestamp=2.0)
        msg3 = Message(source=3, destination=0, timestamp=3.0)

        print("[Action] Enqueueing 2 messages:")
        q.enqueue(msg1)
        q.enqueue(msg2)
        q.print_queue()

        print("[Action] Attempting to enqueue a 3rd message into a full queue:")
        q.enqueue(msg3)

        print("\n[Action] Dequeueing 1 message:")
        q.dequeue()
        q.print_queue()
        print()

    @staticmethod
    def test_server():
        print("--- Testing Server ---")
        server = Server(mu=8)
        server.print_server()

        msg = Message(source=1, destination=0, timestamp=1.5)

        print("\n[Action] Starting service...")
        server.start_service(msg)
        server.print_server()

        print(f"Random service time generated: {server.get_service_time():.3f} seconds")

        print("\n[Action] Ending service...")
        server.end_service()
        server.print_server()
        print()

    @staticmethod
    def test_gateway():
        print("--- Testing Gateway ---")
        scheduler = Scheduler()
        gw = Gateway(mu=8, num_servers=1, queue_capacity=4)
        gw.print_gateway_state()

        # Manually set scheduler time so _start_service uses correct base
        scheduler._current_time = 1.0
        msg1 = Message(source=1, destination=0, timestamp=1.0)
        gw.handle_arrival(msg1, scheduler)

        scheduler._current_time = 2.0
        msg2 = Message(source=1, destination=0, timestamp=2.0)
        gw.handle_arrival(msg2, scheduler)
        gw.print_gateway_state()

        scheduler._current_time = 3.5
        gw.handle_departure(msg1, scheduler)
        gw.print_gateway_state()
        print(f"  Total dropped: {gw.get_dropped_count()}")
        print()

    @staticmethod
    def test_integration():
        print("--- Testing Integrated Simulation (Client -> Gateway -> Queue -> Server) ---")

        scheduler = Scheduler()
        client    = Client(lambda_rate=6)   # 6 msgs/sec arriving
        gateway   = Gateway(mu=8, num_servers=1, queue_capacity=3)

        print("\n[Action] Starting simulation engine...")

        # Seed with the first message
        first_msg   = client.generate_message(current_time=0.0)
        first_event = Event(event_type=EventType.SEND_MSG,
                            event_time=first_msg.get_timestamp(),
                            message=first_msg)
        scheduler.add_event(first_event)

        max_events  = 20
        event_count = 0

        print(f"\n{'time':<9} {'node':<5} {'event':<6} {'source':<6} {'dest.':<5} {'msgID'}")
        print("-" * 50)

        while event_count < max_events:
            current_event = scheduler.get_event()
            if not current_event:
                break

            Main.GenerateTrace(current_event)
            event_count += 1

            e_type       = current_event.get_event_type()
            msg          = current_event.get_message()
            current_time = scheduler.get_current_time()

            if e_type == EventType.SEND_MSG:
                # Message travels to gateway (1-second propagation delay)
                recv_event = Event(event_type=EventType.RECV_MSG,
                                   event_time=current_time + 1.0,
                                   message=msg)
                scheduler.add_event(recv_event)

                # Client generates the NEXT message
                next_msg = client.generate_message(current_time)
                scheduler.add_event(Event(event_type=EventType.SEND_MSG,
                                          event_time=next_msg.get_timestamp(),
                                          message=next_msg))

            elif e_type == EventType.RECV_MSG:
                gateway.handle_arrival(msg, scheduler)

            elif e_type == EventType.MSG_DEPT:
                gateway.handle_departure(msg, scheduler)

        gateway.print_gateway_state()

    # ── Simulation engine ────────────────────────────────────────────────────

    @staticmethod
    def CreateClients(n_clients, lambda_rate, scheduler, sim_time):
        """
        Instantiate n_clients Client objects, seed the scheduler with each
        client's first SEND_MSG event, and return a dict {client_id: Client}.
        """
        clients_map = {}
        for _ in range(n_clients):
            c     = Client(lambda_rate=lambda_rate)
            # generate_message(current_time=0.0) gives absolute timestamp
            msg   = c.generate_message(current_time=0.0)
            if msg.get_timestamp() <= sim_time:
                scheduler.add_event(
                    Event(EventType.SEND_MSG,
                          event_time=msg.get_timestamp(), message=msg))
            clients_map[c.get_client_id()] = c
        return clients_map

    @staticmethod
    def Run(n_clients=1, lambda_rate=4, mu=8,
            num_servers=1, queue_capacity=float('inf'),
            sim_time=500.0, verbose=False):
        """
        Full discrete-event simulation loop.

        Parameters
        ----------
        n_clients     : number of independent client sources
        lambda_rate   : arrival rate per client (msgs/sec)
        mu            : service rate per server (msgs/sec)
        num_servers   : servers in the gateway
        queue_capacity: max messages waiting in queue (inf = M/M/c)
        sim_time      : simulation horizon (seconds)
        verbose       : if True, print trace line for every event

        Returns
        -------
        metrics : Metrics object with all collected statistics
        """

        scheduler   = Scheduler()
        metrics     = Metrics()
        gateway     = Gateway(mu=mu, num_servers=num_servers,
                              queue_capacity=queue_capacity,
                              metrics=metrics)

        clients_map = Main.CreateClients(n_clients, lambda_rate,
                                         scheduler, sim_time)

        if verbose:
            print(f"\n{'time':<9} {'node':<5} {'event':<6} {'source':<6} {'dest.':<5} {'msgID'}")

        # ── Event loop ───────────────────────────────────────────────────────
        while True:
            ev = scheduler.get_event()
            if ev is None:
                break

            t     = ev.get_event_time()
            etype = ev.get_event_type()
            msg   = ev.get_message()

            if t > sim_time:
                break

            # Accumulate ∫N(t)dt for the interval since last event
            metrics.advance_time(t)
            # Sync instant counters from gateway
            metrics.sync_counts(gateway.get_n_system(), gateway.get_n_queue())

            # ── SEND_MSG ─────────────────────────────────────────────────────
            if etype == EventType.SEND_MSG:
                # Schedule RECV_MSG 1 second later (propagation delay)
                recv_time = t + 1.0
                if recv_time <= sim_time:
                    scheduler.add_event(
                        Event(EventType.RECV_MSG, event_time=recv_time, message=msg))

                # Schedule the same client's next SEND_MSG
                client_id = msg.get_source()
                if client_id in clients_map:
                    next_msg = clients_map[client_id].generate_message(current_time=t)
                    if next_msg.get_timestamp() <= sim_time:
                        scheduler.add_event(
                            Event(EventType.SEND_MSG,
                                  event_time=next_msg.get_timestamp(),
                                  message=next_msg))

            # ── RECV_MSG ─────────────────────────────────────────────────────
            elif etype == EventType.RECV_MSG:
                # handle_arrival internally calls metrics.record_arrival()
                # and metrics.record_drop() via the metrics hook in Gateway
                gateway.handle_arrival(msg, scheduler)

            # ── MSG_DEPT ─────────────────────────────────────────────────────
            elif etype == EventType.MSG_DEPT:
                gateway.handle_departure(msg, scheduler)

            if verbose:
                Main.GenerateTrace(ev)

        metrics.finalise(sim_time)
        return metrics


if __name__ == "__main__":
    Main.test_message()
    Main.test_event()
    Main.test_client()
    Main.test_queue()
    Main.test_server()
    Main.test_gateway()
    Main.test_integration()

    print("=== Smoke-test: M/M/1  lambda=4  mu=8  T=100 ===")
    m = Main.Run(n_clients=1, lambda_rate=4, mu=8,
                 num_servers=1, queue_capacity=float('inf'),
                 sim_time=100.0, verbose=True)
    m.print_summary()
