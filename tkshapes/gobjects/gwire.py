
from ..gobject import GObject
from ..gitem import GWireItem
from ..gconnection import GConnection


class GWire(GObject):
    """ Draw Wire connecting two connectable GObjects """

    def __init__(self, *args, **kwargs):
        initial_coords = args[0]  # should be a 4-tuple
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(0, 0, name_tag)

        # We are a connector object (used for connecting two connectable GObjects)
        self.connector = True

        # Connector GObjects keep track of what they are connected to
        self.connection = GConnection(name=name_tag, g_object=self)

        # As the GWire will need to move with other objects are they are re-positioned
        # we will need to remember and track the two end points, and also implement
        # methods to move and redraw.
        self._coords = initial_coords

    def add(self):

        coords = self.smooth_coords(self._coords)

        # We draw a fat line first, and then draw a thicker white line on top to
        # make it look like a wire.
        self._items['fat_line'] = GWireItem(self.gcanvas, coords, self._tag)
        self._items['fat_line'].add()
        self._items['fat_line'].outline_color = 'blue'
        self._items['fat_line'].outline_width = 5.0 * self.gcanvas.zoom_level
        self._items['fat_line'].hidden = False
        self._items['fat_line'].draggable = False
        self._items['fat_line'].always_on_top = True

        self._items['thin_line'] = GWireItem(self.gcanvas, coords, self._tag)
        self._items['thin_line'].add()
        self._items['thin_line'].outline_color = 'white'
        self._items['thin_line'].outline_width = 2.0 * self.gcanvas.zoom_level
        self._items['thin_line'].hidden = False
        self._items['thin_line'].draggable = False
        self._items['thin_line'].always_on_top = True

    def coords(self, coords):
        self._coords = coords

    def redraw(self):
        for g_item_name in self._items:
            g_item = self._items[g_item_name]
            g_item.coords = self.smooth_coords(self._coords)
            g_item.redraw()

    def move_to(self, coords):
        self.coords(coords)
        self.redraw()

    def update(self):
        """ check if we have any GNode connections, update our coords, and redraw """
        coords = []
        if self.connection.g_nodes:
            #print(f"** DEBUG: {self}")
            #print(f"** DEBUG: {self.connection}")
            #print(f"** DEBUG: {self.connection.g_nodes}")
            for g_node in self.connection.g_nodes:
                #print(f"** DEBUG:      g_node.name: {g_node.name}")
                #print(f"** DEBUG:      g_node.g_item: {g_node.g_item} {g_node.g_item.item}")
                (x, y) = g_node.g_item.center_point()
                coords.extend([x, y])
            #print(f"DEBUG: update(): Calculated new coords for GWire {coords}")
            self.move_to(coords)

