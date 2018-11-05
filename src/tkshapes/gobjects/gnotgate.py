
from ..gobject import GObject
from ..gitem import GHorzLineItem, GOvalItem, GPolygonItem
from ..gnode import GNode


class GNotGate(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []

    def add(self):
        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 66, self._y + 28, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 76, self._y + 23, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GNotGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line'] = GHorzLineItem(self.gcanvas, self._x, self._y + 28, -10, self._tag)
        self._items['input_line'].add()
        self._items['input_line'].hidden = False
        self._items['input_line'].draggable = False

        self._items['input_dot'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 23, 10, 10, self._tag)
        self._items['input_dot'].add()
        self._items['input_dot'].fill_color = 'white'
        self._items['input_dot'].outline_color = 'blue'
        self._items['input_dot'].active_outline_color = 'orange'
        self._items['input_dot'].outline_width = 2.0
        self._items['input_dot'].active_outline_width = 5.0
        self._items['input_dot'].hidden = False
        self._items['input_dot'].draggable = False
        self._items['input_dot'].show_selection = False
        self._items['input_dot'].connectable_terminator = True

        self._nodes['input'] = GNode(name="GNotGate Input", g_object=self, g_item=self._items['input_dot'])

        self._items['not_dot'] = GOvalItem(self.gcanvas, self._x + 58, self._y + 24, 8, 8, self._tag)
        self._items['not_dot'].add()
        self._items['not_dot'].fill_color = 'white'
        self._items['not_dot'].outline_color = 'blue'
        self._items['not_dot'].active_outline_color = 'orange'
        self._items['not_dot'].outline_width = 2.0
        self._items['not_dot'].active_outline_width = 5.0
        self._items['not_dot'].hidden = False
        self._items['not_dot'].draggable = False
        self._items['not_dot'].show_selection = True
        self._items['not_dot'].highlight_group = 'body_plus_not_bubble'

        self._points.extend((self._x, self._y))  # first point in polygon
        self._points.extend((self._x + 58, self._y + 28))
        self._points.extend((self._x + 0, self._y + 56))

        self._items['body'] = GPolygonItem(self.gcanvas, self._points, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True
        self._items['body'].highlight_group = 'body_plus_not_bubble'

