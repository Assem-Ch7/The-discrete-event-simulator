# queue.py
from collections import deque
from message import Message

class Queue:
    """
    FIFO message buffer with configurable capacity.
    Used by the Gateway to hold messages waiting for server processing.
    """
    def __init__(self, max_size=float('inf')):
        # Use deque for O(1) append/pop operations
        self._messages = deque()
        # max_size = float('inf') for M/M/1, integer (4, 8) for finite buffers
        self._max_size = max_size
        print(f"[LOG] Queue initialized | Capacity: {self._max_size}")

    def enqueue(self, message: Message) -> bool:
        """
        Add a message to the back of the queue.
        Returns True if added successfully, False if queue is full (message dropped).
        """
        if self.is_full():
            print(f"[LOG] QUEUE FULL | Dropping message ID: {message.get_message_id()}")
            return False  # Engine/Gateway should increment drop counter when False

        self._messages.append(message)
        print(f"[LOG] ENQUEUE | MsgID: {message.get_message_id()} | New size: {self.size()}")
        return True

    def dequeue(self) -> Message | None:
        """
        Remove and return the front message (FIFO).
        Returns None if queue is empty.
        """
        if self.is_empty():
            print("[LOG] QUEUE EMPTY | Cannot dequeue.")
            return None

        message = self._messages.popleft()
        print(f"[LOG] DEQUEUE | MsgID: {message.get_message_id()} | Remaining: {self.size()}")
        return message

    def is_full(self) -> bool:
        """Check if queue has reached its maximum capacity."""
        return len(self._messages) >= self._max_size

    def is_empty(self) -> bool:
        """Check if queue contains no messages."""
        return len(self._messages) == 0

    def size(self) -> int:
        """Return current number of waiting messages."""
        return len(self._messages)

    def print_queue(self) -> None:
        """Debug helper: prints all messages currently in the buffer."""
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
