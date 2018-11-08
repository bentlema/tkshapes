
class GConnection:

    gconn_id = 1_000_000_000

    def __init__(self, name, g_object):
        self.id = self.next_id()
        self.name = name
        self.g_object = g_object
        self.g_nodes = []
        self.max_nodes = 2

    def next_id(self):
        GConnection.gconn_id += 1
        return GConnection.gconn_id

