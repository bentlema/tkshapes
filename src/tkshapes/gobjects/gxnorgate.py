import math

from ..gobject import GObject
from ..gitem import GOvalItem, GPolygonItem, GHorzLineItem
from ..gnode import GNode


class GXNorGate(GObject):
    """ Draw XOR Gate on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._arc1_points = []
        self._arc2_points = []

    def add(self):

        x = self._x
        y = self._y

        self._arc1_points.extend((x, y))  # first point in polygon

        # scale the unit circle by 30, as that's the distance from the center of the circle to the arc
        # See Also: https://en.wikipedia.org/wiki/Unit_circle
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 65) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc1_points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc1_points.extend((arc_x, arc_y))

        # Arc2 is the extra line on the back of the XOR gate
        self._arc2_points.extend((x - 8, y))  # first point in polygon

        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 8) + (x - 8)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc2_points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + (x - 8)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc2_points.extend((arc_x, arc_y))

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 74, self._y + 30, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 84, self._y + 25, 10, 10, self._tag)
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

        self._nodes['output'] = GNode(name="GXOrGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line1'] = GHorzLineItem(self.gcanvas, self._x, self._y + 17, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 12, 10, 10, self._tag)
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

        self._nodes['input_1'] = GNode(name="GXOrGate Input 1", g_object=self, g_item=self._items['input_dot1'])

        self._items['input_line2'] = GHorzLineItem(self.gcanvas, self._x, self._y + 43, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 38, 10, 10, self._tag)
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

        self._nodes['input_2'] = GNode(name="GXOrGate Input 2", g_object=self, g_item=self._items['input_dot2'])

        self._items['not_dot'] = GOvalItem(self.gcanvas, self._x + 66, self._y + 26, 8, 8, self._tag)
        self._items['not_dot'].add()
        self._items['not_dot'].fill_color = 'white'
        self._items['not_dot'].outline_color = 'blue'
        self._items['not_dot'].active_outline_color = 'orange'
        self._items['not_dot'].outline_width = 2.0
        self._items['not_dot'].active_outline_width = 5.0
        self._items['not_dot'].hidden = False
        self._items['not_dot'].draggable = False
        self._items['not_dot'].show_selection = True
        self._items['not_dot'].highlight_group = 'body_plus_arc2'

        self._items['body'] = GPolygonItem(self.gcanvas, self._arc1_points, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True
        self._items['body'].highlight_group = 'body_plus_arc2'

        self._items['arc2'] = GPolygonItem(self.gcanvas, self._arc2_points, self._tag)
        self._items['arc2'].add()
        self._items['arc2'].fill_color = 'white'
        self._items['arc2'].outline_color = 'blue'
        self._items['arc2'].active_outline_color = 'orange'
        self._items['arc2'].outline_width = 2.0
        self._items['arc2'].active_outline_width = 5.0
        self._items['arc2'].hidden = False
        self._items['arc2'].draggable = True
        self._items['arc2'].show_selection = False
        self._items['arc2'].highlight_group = 'body_plus_arc2'

