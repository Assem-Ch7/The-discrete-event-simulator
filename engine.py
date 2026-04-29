# create events and show me the trace of the events
# we don't need meain for engine, jsut put test functions 

from message import Message
from event import Event, EventType
from scheduler import Scheduler

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
        event5 = Event(event_type=EventType.DEPT_MSG, event_time=4.572, message=msg1)
        event6 = Event(event_type=EventType.DEPT_MSG, event_time=5.916, message=msg2)

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

if __name__ == "__main__":
    #Main.test_message()
    Main.test_event()