from collections import deque
from message import Message

class Queue:
    def __init__(self, max_size=float('inf')):
        self._messages = deque()
        self._max_size = max_size
        print(f"Queue initialized | Capacity: {self._max_size}")

    def enqueue(self, message: Message) -> bool:
        if self.is_full():
            print(f"QUEUE FULL | Dropping message ID: {message.get_message_id()}")
            return False
        self._messages.append(message)
        print(f"ENQUEUE | MsgID: {message.get_message_id()} | New size: {self.size()}")
        return True

    def dequeue(self) -> Message | None:
        if self.is_empty():
            print("QUEUE EMPTY | Cannot dequeue.")
            return None

        message = self._messages.popleft()
        print(f"DEQUEUE | MsgID: {message.get_message_id()} | Remaining: {self.size()}")
        return message

    def is_full(self) -> bool:
        return len(self._messages) >= self._max_size

    def is_empty(self) -> bool:  
        return len(self._messages) == 0

    def size(self) -> int:
        return len(self._messages)

    def print_queue(self) -> None:
        print(f"\n{'='*30} QUEUE STATE {'='*30}")
        print(f"Capacity: {self._max_size} | Current Size: {self.size()}")
        if self.is_empty():
            print("[ EMPTY ]")
        else:
            for i, msg in enumerate(self._messages, 1):
                print(f"  Pos {i}: MsgID={msg.get_message_id()} | "
                      f"Source={msg.get_source()} | Dest={msg.get_destination()} | "
                      f"Time={msg.get_timestamp():.3f}")
        print("="*71 + "\n")
