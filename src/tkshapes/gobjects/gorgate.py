
import math

from ..gobject import GObject
from ..gitem import GHorzLineItem, GOvalItem, GPolygonItem
from ..gnode import GNode


class GOrGate(GObject):
    """ Draw OR Gate on the GCanvas """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._points = []

    def add(self):

        x = self._x
        y = self._y

        self._points.extend((x, y))  # first point in polygon

        # scale the unit circle by 30, as that's the distance from the center of the circle to the arc
        # See Also: https://en.wikipedia.org/wiki/Unit_circle
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 65) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 65, self._y + 30, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 75, self._y + 25, 10, 10, self._tag)
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

        self._nodes['output'] = GNode(name="GOrGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line1'] = GHorzLineItem(self.gcanvas, self._x + 7, self._y + 17, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 13, self._y + 12, 10, 10, self._tag)
        self._items['input_dot1'].add()
        self._items['input_dot1'].fill_color = 'white'
        self._items['input_dot1'].outline_color = 'blue'
        self._items['input_dot1'].active_outline_color = 'orange'
        self._items['input_dot1'].outline_width = 2.0
        self._items['input_dot1'].active_outline_width = 5.0
        self._items['input_dot1'].hidden = False
        self._items['input_dot1'].draggable = False
        self._items['input_dot1'].show_selection = False
        self._items['input_dot1'].connectable_terminator = True

        self._nodes['input_1'] = GNode(name="GOrGate Input 1", g_object=self, g_item=self._items['input_dot1'])

        self._items['input_line2'] = GHorzLineItem(self.gcanvas, self._x + 7, self._y + 43, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 13, self._y + 38, 10, 10, self._tag)
        self._items['input_dot2'].add()
        self._items['input_dot2'].fill_color = 'white'
        self._items['input_dot2'].outline_color = 'blue'
        self._items['input_dot2'].active_outline_color = 'orange'
        self._items['input_dot2'].outline_width = 2.0
        self._items['input_dot2'].active_outline_width = 5.0
        self._items['input_dot2'].hidden = False
        self._items['input_dot2'].draggable = False
        self._items['input_dot2'].show_selection = False
        self._items['input_dot2'].connectable_terminator = True

        self._nodes['input_2'] = GNode(name="GOrGate Input 2", g_object=self, g_item=self._items['input_dot2'])

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

