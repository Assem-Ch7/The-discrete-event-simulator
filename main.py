# create events and show me the trace of the events
# we don't need meain for engine, jsut put test functions 

# main.py
from message import Message
from event import Event, EventType
from scheduler import Scheduler

class Main:
    @staticmethod
    def generate_trace(time, node, event_type, source, dest, msg_id):
        print(f"{time:<8} | {node:<6} | {event_type:<6} | {source:<6} | {dest:<5} | {msg_id}")

    @staticmethod
    def test_message():
        print("--- Testing Message ---")
        msg1 = Message(source=0, destination=1, timestamp=1.202)
        msg2 = Message(source=0, destination=3, timestamp=1.500)
        
        msg1.print_message()
        msg2.print_message() # This will automatically have ID 2
        print()

    @staticmethod
    def test_event():
        """
        Test function for the Event and Scheduler classes.
        """
        print("--- Testing Event & Scheduler ---")
        
        msg1 = Message(source=0, destination=1, timestamp=1.202)
        msg2 = Message(source=0, destination=3, timestamp=2.320)

        event1 = Event(event_type=EventType.SEND_MSG, event_time=1.202, message=msg1)
        event2 = Event(event_type=EventType.SEND_MSG, event_time=2.320, message=msg2)
        event3 = Event(event_type=EventType.RECV_MSG, event_time=1.916, message=msg1)

        # Initialize scheduler and add events
        scheduler = Scheduler()
        scheduler.add_event(event2)
        scheduler.add_event(event1)
        scheduler.add_event(event3)

        # Print Trace Header
        print(f"{'time':<8} | {'node':<6} | {'event':<6} | {'source':<6} | {'dest.':<5} | {'msgID'}")
        print("-" * 55)

        # Process events chronologically
        while True:
            current_event = scheduler.get_event()
            if not current_event:
                break
            
            e_time = current_event.get_event_time()
            e_type = current_event.get_event_type().value
            msg = current_event.get_message()
            
            # Determine node based on trace logic
            node = "1" if e_type == "SEND" and msg.get_message_id() == 1 else "0"

            # Generate the trace for this event by calling Main.generate_trace
            Main.generate_trace(
                time=f"{e_time:.3f}", 
                node=node, 
                event_type=e_type, 
                source=msg.get_source(), 
                dest=msg.get_destination(), 
                msg_id=msg.get_message_id()
            )

# The Main entry point
if __name__ == "__main__":
    Main.test_message()
    Main.test_event()