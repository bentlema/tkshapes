
class GNode:

    # Class variable to keep track of next available ID
    previous_id = 1_000_000_000

    def __init__(self, name, g_object, g_item):
        self.id = self.next_id()
        self.name = name
        self.g_object = g_object
        self.g_item = g_item
        self.connections = []
        self.max_connections = 1

    def next_id(self):
        GNode.previous_id += 1
        return GNode.previous_id

