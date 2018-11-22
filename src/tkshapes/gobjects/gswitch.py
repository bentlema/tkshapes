import math

from ..gobject import GObject
from ..gitem import GHorzLineItem, GOvalItem, GPolygonItem
from ..gnode import GNode


class GToggleSwitch(GObject):
    """ Draw a Toggle Switch on the GCanvas """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._size = 16
        self._capsule_length = self._size + (self._size * 1.5)
        self._points1 = []
        self._points2 = []

        # toggleable items have state that controls some GItems position
        # Note: do not change this initial default, as we assume that the switch
        # is initially off when we draw it below, and toggle() depends on that
        self._state = False

    def add(self):

        x = self._x
        y = self._y

        self._points1.extend((x, y))  # first point in polygon

        # the right side of the capsule
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * self._size) + (x + self._capsule_length)
            arc_y = (math.sin(math.radians(angle)) * self._size) + (y + self._size)
            self._points1.extend((arc_x, arc_y))

        # the left side of the capsule
        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * self._size) + x
            arc_y = (math.sin(math.radians(angle)) * self._size) + (y + self._size)
            self._points1.extend((arc_x, arc_y))

        # the points for the inner capsule (same as above but slightly smaller)
        shrink = self._size * 0.125
        self._points2.extend((x, y + 2 * shrink))  # first point in polygon

        # the right side of the inner capsule
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * (self._size - 2 * shrink)) + (x + self._capsule_length)
            arc_y = (math.sin(math.radians(angle)) * (self._size - 2 * shrink)) + (y + self._size)
            self._points2.extend((arc_x, arc_y))

        # the left side of the inner capsule
        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * (self._size - 2 * shrink)) + x
            arc_y = (math.sin(math.radians(angle)) * (self._size - 2 * shrink)) + (y + self._size)
            self._points2.extend((arc_x, arc_y))

        self._items['output_line'] = GHorzLineItem(
            self.gcanvas, self._x + self._size + self._capsule_length, self._y + self._size, 10, self._tag)

        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(
            self.gcanvas, self._x + self._size + self._capsule_length + 10, self._y + self._size - 5, 10, 10, self._tag)

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

        self._nodes['output'] = GNode(name="GToggleSwitch Output", g_object=self, g_item=self._items['output_dot'])

        self._items['body'] = GPolygonItem(self.gcanvas, self._points1, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 2.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True
        self._items['body'].highlight_group = "body_and_slider"

        self._items['inner'] = GPolygonItem(self.gcanvas, self._points2, self._tag)
        self._items['inner'].add()
        self._items['inner'].fill_color = '#777777'
        self._items['inner'].outline_color = 'blue'
        self._items['inner'].active_outline_color = 'blue'
        self._items['inner'].outline_width = 0.25
        self._items['inner'].active_outline_width = 0.25
        self._items['inner'].hidden = False
        self._items['inner'].draggable = True
        self._items['inner'].show_selection = False
        self._items['inner'].highlight_group = "body_and_slider"

        self._items['slider_switch'] = GOvalItem(
            self.gcanvas,
            self._x + self._capsule_length - (self._size - self._size * 0.2), self._y + int(self._size * 0.2),
            (self._size - int(self._size * 0.2)) * 2,
            (self._size - int(self._size * 0.2)) * 2,
            self._tag)

        self._items['slider_switch'].add()
        self._items['slider_switch'].fill_color = 'white'
        self._items['slider_switch'].outline_color = 'blue'
        self._items['slider_switch'].active_outline_color = 'blue'
        self._items['slider_switch'].outline_width = 1.0
        self._items['slider_switch'].active_outline_width = 1.0
        self._items['slider_switch'].hidden = False
        self._items['slider_switch'].draggable = False
        self._items['slider_switch'].clickable = True
        self._items['slider_switch'].highlight_group = "body_and_slider"

    def toggle(self):
        if self._state:
            #print(f"DEBUG: Switch = ON --> OFF")
            self.state = False
        else:
            #print(f"DEBUG: Switch = OFF --> ON")
            self.state = True

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value and not self._state:
            # adjust the item for True/ON
            dx = -1 * self._capsule_length * self.gcanvas.zoom_level
            #print(f"DEBUG: Switch = OFF --> ON {dx}")
            self._items['inner'].fill_color = 'green'
            self._state = True
            self._move_slider(dx)
        elif not value and self._state:
            # adjust the item for False/OFF
            dx = self._capsule_length * self.gcanvas.zoom_level
            #print(f"DEBUG: Switch = ON --> OFF {dx}")
            self._items['inner'].fill_color = '#777777'
            self._state = False
            self._move_slider(dx)

    def _move_slider(self, dx):
        steps = 5
        step_length = dx / steps
        for step in range(steps):
            position = step_length
            self.gcanvas.canvas.move(self._items['slider_switch'].item, position, 0)
            # TODO: This is a quick hack to animate the slider, and works fine as we have a small number of steps
            # TODO: However, we should eventually re-do any animation to use the after() method as discussed on
            # TODO: these StackOverflow pages:
            # TODO:
            # TODO: https://stackoverflow.com/questions/21357178/python-tkinter-refresh-canvas
            # TODO: https://stackoverflow.com/questions/25430786/moving-balls-in-tkinter-canvas/25431690#25431690
            self.gcanvas.canvas.update_idletasks()

