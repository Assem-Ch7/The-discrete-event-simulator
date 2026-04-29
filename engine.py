from message import Message
from event import Event, EventType
from scheduler import Scheduler
from client import Client
from server import Server
from queue import Queue
from gateway import Gateway

class Main:
    @staticmethod
    def GenerateTrace(e):
        e_time = e.get_event_time()
        e_type = e.get_event_type().value
        msg = e.get_message()
        
        if e_type == "SEND":
                node = msg.get_source()
        elif e_type == "RECV":
                node = msg.get_destination() 
        else:
                node = "0"

        print(f"{e_time:<7.3f} {node:<5} {e_type:<6} {msg.get_source():<6} {msg.get_destination():<5} {msg.get_message_id()}")

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
        scheduler.add_event(event4)
        scheduler.add_event(event1)
        scheduler.add_event(event6)
        scheduler.add_event(event2)
        scheduler.add_event(event5)
        scheduler.add_event(event3)

        print(f"{'time':<7} {'node':<5} {'event':<6} {'source':<6} {'dest.':<5} {'msgID'}")

        while True:
            current_event = scheduler.get_event()
            if not current_event:
                break
            
            Main.GenerateTrace(current_event)

    @staticmethod
    def test_client():
        print("--- Testing Client ---")
        # Initialize client with lambda = 4 (from M/M/1 example)
        client = Client(lambda_rate=4)
        client.print_client()
        
        print("\nGenerating consecutive messages:")
        # We start at time 0.0, and the client generates the next interval
        msg1 = client.generate_message(current_time=0.0, destination=2)
        msg2 = client.generate_message(current_time=msg1.get_timestamp(), destination=3)
        
        msg1.print_message()
        msg2.print_message()
        print()

    @staticmethod
    def test_server():
        print("--- Testing Server ---")
        # Initialize server with mu = 8
        server = Server(mu=8)
        server.print_server()
        
        # Create a dummy message to feed the server
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
    def test_integration():
        print("--- Testing Integrated Simulation (Client -> Gateway -> Queue -> Server) ---")
        
        # 1. Initialize the core components
        scheduler = Scheduler()
        client = Client(lambda_rate=6) # 6 messages arriving per second
        gateway = Gateway(mu=8, num_servers=1, queue_capacity=3) # Server processes 8/sec, max queue of 3
        
        print("\n[Action] Starting simulation engine...")
        
        # 2. Kickstart the simulation with the first message
        first_msg = client.generate_message(current_time=0.0)
        first_event = Event(event_type=EventType.SEND_MSG, event_time=first_msg.get_timestamp(), message=first_msg)
        scheduler.add_event(first_event)
        
        # 3. Event Loop
        max_events = 20
        event_count = 0
        
        print(f"\n{'time':<7} {'node':<5} {'event':<6} {'source':<6} {'dest.':<5} {'msgID'}")
        print("-" * 50)
        
        while event_count < max_events:
            current_event = scheduler.get_event()
            if not current_event:
                break
                
            Main.GenerateTrace(current_event)
            event_count += 1
            
            e_type = current_event.get_event_type()
            msg = current_event.get_message()
            current_time = scheduler.get_current_time()
            
            # --- THE LOGIC ROUTER ---
            if e_type == EventType.SEND_MSG:
                # A. Message travels to gateway (takes 1.0 second as per slides)
                recv_time = current_time + 1.0
                recv_event = Event(event_type=EventType.RECV_MSG, event_time=recv_time, message=msg)
                scheduler.add_event(recv_event)
                
                # B. Client generates the NEXT message to keep traffic flowing
                next_msg = client.generate_message(current_time)
                next_send_event = Event(event_type=EventType.SEND_MSG, event_time=next_msg.get_timestamp(), message=next_msg)
                scheduler.add_event(next_send_event)
                
            elif e_type == EventType.RECV_MSG:
                # Gateway receives the message, tries to pass to Server or puts in Queue
                gateway.handle_arrival(msg, scheduler)
                
            elif e_type == EventType.MSG_DEPT:
                # Message leaves Server, Gateway pulls next from Queue
                gateway.handle_departure(msg, scheduler)

        # 4. Show the final state after 20 events
        gateway.print_gateway_state()

if __name__ == "__main__":
    # Main.test_message()
    # Main.test_event()
    # Main.test_client()
    # Main.test_server()
    # Main.test_queue()
    Main.test_integration()