
import math
import cmath
import itertools

from ..gobject import GObject
from ..gitem import GPolygonItem


class GPythonLogo(GObject):
    """ Draw Python Logo on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []
        self._rotated_points = []
        self._zoomed_points = []
        self._zoomed_rotated_points = []

    def add(self):

        x = self._x
        y = self._y

        self._points.extend((x, y + 68))  # first point in polygon

        # starting at top left snake mouth
        for angle in range(-180, -90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 29)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(-90, 0):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 126)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(0, 90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 126)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 122)
            self._points.extend((arc_x, arc_y))

        for angle in range(-90, 0):
            arc_x = (math.cos(math.radians(angle)) * -42) + (x + 30)
            arc_y = (math.sin(math.radians(angle)) * 42) + (y + 194)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x - 12, y + 238))

        for angle in range(90, 180):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x - 50)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 208)
            self._points.extend((arc_x, arc_y))

        for angle in range(-180, -90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x - 50)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 110)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x + 78, y + 80))
        self._points.extend((x + 78, y + 68))
        self._points.extend((x + 32, y + 68))
        self._points.extend((x + 32, y + 50))

        for angle in range(-270, 90):
            arc_x = (math.cos(math.radians(angle)) * 15) + (x + 32)
            arc_y = (math.sin(math.radians(angle)) * 15) + (y + 32)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x + 32, y + 68))

        # the mathematical formulas to scale a point (x,y) by a factor of S relative to the point (cx, cy) are:
        # x_new = (S * (x - cx)) + cx
        # y_new = (S * (y - cy)) + cy

        cx = x + 78
        cy = y + 158

        self._zoomed_points = []
        for xx, yy in grouper(self._points, 2):
            x_new = (self.gcanvas.zoom_level * (xx - cx)) + cx
            y_new = (self.gcanvas.zoom_level * (yy - cy)) + cy
            self._zoomed_points.extend((x_new, y_new))

        self._items['blue_snake'] = GPolygonItem(self.gcanvas, self._zoomed_points, self._tag)
        self._items['blue_snake'].add()
        self._items['blue_snake'].fill_color = '#4B8BBE'
        self._items['blue_snake'].outline_color = '#4B8BBE'
        self._items['blue_snake'].active_outline_color = '#4B8BBE'
        self._items['blue_snake'].outline_width = 1.0
        self._items['blue_snake'].active_outline_width = 1.0
        self._items['blue_snake'].hidden = False
        self._items['blue_snake'].draggable = True
        self._items['blue_snake'].show_selection = False
        self._items['blue_snake'].show_highlight = False

        # I want to make a second snake rotated 180 degrees
        # See: http://effbot.org/zone/tkinter-complex-canvas.htm
        angle = 3.14159  # 3.14159 radians = 180 degrees
        cangle = cmath.exp(angle * 1j)

        # we will rotate about x,y
        center = complex(cx, cy)
        self._rotated_points = []
        for xx, yy in grouper(self._points, 2):
            v = cangle * (complex(xx, yy) - center) + center
            self._rotated_points.extend((v.real, v.imag))

        self._zoomed_rotated_points = []
        for xx, yy in grouper(self._rotated_points, 2):
            x_new = (self.gcanvas.zoom_level * (xx - cx)) + cx
            y_new = (self.gcanvas.zoom_level * (yy - cy)) + cy
            self._zoomed_rotated_points.extend((x_new, y_new))

        self._items['orange_snake'] = GPolygonItem(self.gcanvas, self._zoomed_rotated_points, self._tag)
        self._items['orange_snake'].add()
        self._items['orange_snake'].fill_color = '#FFD43B'
        self._items['orange_snake'].outline_color = '#FFD43B'
        self._items['orange_snake'].active_outline_color = '#FFD43B'
        self._items['orange_snake'].outline_width = 1.0
        self._items['orange_snake'].active_outline_width = 1.0
        self._items['orange_snake'].hidden = False
        self._items['orange_snake'].draggable = True
        self._items['orange_snake'].show_selection = False
        self._items['orange_snake'].show_highlight = False


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    Example:  grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

