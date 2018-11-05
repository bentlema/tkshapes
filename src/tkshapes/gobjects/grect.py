
from ..gobject import GObject
from ..gitem import GRectItem


class GRect(GObject):
    """ Draw Square or Rectangle on a GCanvas """

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        width = args[2]
        height = args[3]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        # attributes unique to a GRect
        self._width = width
        self._height = height

    def add(self):

        # Adjust width and height for current zoom level
        self._width *= self.gcanvas.zoom_level
        self._height *= self.gcanvas.zoom_level

        self._items['GRect'] = GRectItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['GRect'].add()
        self._items['GRect'].fill_color = 'white'
        self._items['GRect'].outline_color = 'blue'
        self._items['GRect'].active_outline_color = 'orange'
        self._items['GRect'].outline_width = 2.0 * self.gcanvas.zoom_level
        self._items['GRect'].active_outline_width = 5.0 * self.gcanvas.zoom_level
        self._items['GRect'].hidden = False
        self._items['GRect'].draggable = True
        self._items['GRect'].show_selection = True


