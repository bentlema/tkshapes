import math

from ..gobject import GObject
from ..gitem import GHorzLineItem, GVertLineItem, GOvalItem, GPolygonItem
from ..gnode import GNode


class GLightBulb(GObject):
    """ Draw a Light Bulb on the GCanvas """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._bulb_size = 30
        self._base_size = self._bulb_size + (self._bulb_size * 0.6)
        self._points1 = []
        self._points2 = []

        # toggleable items have state that controls some GItems position or colors
        # Note: do not change this initial default, as we assume that the bulb
        # is initially off when we draw it below, and toggle() depends on that
        self._state = False

    def add(self):

        x = self._x
        y = self._y

        self._points1.extend((x + (self._base_size * 0.2), y))  # first point in polygon
        self._points1.extend((x - (self._base_size * 0.2), y))

        # the right side of the capsule
        for angle in range(-250, 70):
            arc_x = (math.cos(math.radians(angle)) * self._bulb_size) + x
            arc_y = (math.sin(math.radians(angle)) * self._bulb_size) + (y - self._base_size)
            self._points1.extend((arc_x, arc_y))

        self._items['input_line'] = GVertLineItem(
            self.gcanvas, self._x, self._y, 10, self._tag)

        self._items['input_line'].add()
        self._items['input_line'].hidden = False
        self._items['input_line'].draggable = False

        self._items['input_dot'] = GOvalItem(
            self.gcanvas, self._x - 5, self._y + 10, 10, 10, self._tag)

        self._items['input_dot'].add()
        self._items['input_dot'].fill_color = 'white'
        self._items['input_dot'].outline_color = 'blue'
        self._items['input_dot'].active_outline_color = 'orange'
        self._items['input_dot'].outline_width = 2.0
        self._items['input_dot'].active_outline_width = 5.0
        self._items['input_dot'].hidden = False
        self._items['input_dot'].draggable = False
        self._items['input_dot'].connectable_initiator = False
        self._items['input_dot'].connectable_terminator = True
        self._items['input_dot'].show_selection = False

        self._nodes['input'] = GNode(name="GLightBulb Input", g_object=self, g_item=self._items['input_dot'])

        self._items['body'] = GPolygonItem(self.gcanvas, self._points1, self._tag, smooth=1, splinesteps=16)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 2.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].clickable = False
        self._items['body'].show_selection = True
        self._items['body'].highlight_group = "body_and_filament"

        self._points2.extend((x + (self._base_size * 0.10), y - self._base_size / 2.3))
        self._points2.extend((x - (self._base_size * 0.10), y - self._base_size / 2.3))
        self._points2.extend((x - (self._base_size * 0.05), y - self._base_size / 2))
        self._points2.extend((x - (self._base_size * 0.20), y - self._base_size))
        self._points2.extend((x + (self._base_size * 0.20), y - self._base_size))
        self._points2.extend((x + (self._base_size * 0.05), y - (self._base_size / 2)))

        self._items['filament'] = GPolygonItem(self.gcanvas, self._points2, self._tag, smooth=0)
        self._items['filament'].add()
        self._items['filament'].fill_color = 'white'
        self._items['filament'].outline_color = 'blue'
        self._items['filament'].active_outline_color = 'blue'
        self._items['filament'].outline_width = 1.0
        self._items['filament'].active_outline_width = 1.0
        self._items['filament'].hidden = False
        self._items['filament'].draggable = True
        self._items['filament'].clickable = False
        self._items['filament'].show_selection = False
        self._items['filament'].highlight_group = "body_and_filament"

    def toggle(self):
        if self._state:
            print(f"DEBUG: LightBulb = ON --> OFF")
            self.state = False
        else:
            print(f"DEBUG: LightBulb = OFF --> ON")
            self.state = True

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value and not self._state:
            self._items['filament'].fill_color = '#FFFF00'  # yellow
            self._items['filament'].outline_color = '#FF8000'  # orange
            self._items['filament'].active_outline_color = '#FF8000'
            self._items['body'].fill_color = '#FFFF00'
            self._state = True
        elif not value and self._state:
            self._items['filament'].fill_color = 'white'
            self._items['filament'].outline_color = 'blue'
            self._items['filament'].active_outline_color = 'blue'
            self._items['body'].fill_color = 'white'
            self._state = False



