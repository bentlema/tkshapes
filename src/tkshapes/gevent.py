import queue

class GEvent:
    """ docstring """

    g_event_id = 1_000_000_000

    def __init__(self, event_type, event_data):
        """ Initialize a GEvent given event_type and event_data """

        # A unique numerical identifier assigned to the event
        self.event_id = self.next_id()

        # A string identifying the event type
        self.event_type = str(event_type)

        # Each event_type can have it's own associated data
        self.event_data = event_data

    @staticmethod
    def next_id():
        """ return the next available ID """
        GEvent.g_event_id += 1
        return GEvent.g_event_id


class GEventQueue:
    """ the event queue can hold GEvent objects """

    def __init__(self, name, maxsize=100):
        self.name = str(name)
        self.events = queue.Queue(maxsize=maxsize)

    def get_event(self):
        try:
            return self.events.get_nowait()
        except queue.Empty:
            pass
        return None

    def put_event(self, g_event):
        if type(g_event) != GEvent:
            raise TypeError
        try:
            self.events.put_nowait(g_event)
            return True
        except queue.Full:
            pass
        return False

    def get_qsize(self):
        return self.events.qsize()

    def is_empty(self):
        return self.events.empty()

    def is_full(self):
        return self.events.full()

