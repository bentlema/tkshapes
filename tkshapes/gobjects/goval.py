
from ..gobject import GObject
from ..gitem import GOvalItem


class GOval(GObject):
    """ Draw Oval or Circle on a GCanvas """

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        width = args[2]
        height = args[3]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        # attributes unique to a GOval
        self._width = width
        self._height = height

    def add(self):

        # Adjust width and height for current zoom level
        self._width *= self.gcanvas.zoom_level
        self._height *= self.gcanvas.zoom_level

        self._items['GOval'] = GOvalItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['GOval'].add()
        self._items['GOval'].fill_color = 'white'
        self._items['GOval'].outline_color = 'blue'
        self._items['GOval'].active_outline_color = 'orange'
        self._items['GOval'].outline_width = 2.0 * self.gcanvas.zoom_level
        self._items['GOval'].active_outline_width = 5.0 * self.gcanvas.zoom_level
        self._items['GOval'].hidden = False
        self._items['GOval'].draggable = True
        self._items['GOval'].show_selection = True

