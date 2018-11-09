
from ..gobject import GObject
from ..gitem import GPolygonItem
from ..gnode import GNode


class GPolygon(GObject):
    """ Draw Polygon given coords GCanvas """

    def __init__(self, *args, **kwargs):
        super().__init__(0, 0, **kwargs)

        if 'coords' in kwargs:
            self._coords = kwargs['coords']
        else:
            self._coords = []

    def add(self):

        self._items['polygon'] = GPolygonItem(self.gcanvas, self._coords, self._tag)
        self._items['polygon'].add()
        self._items['polygon'].fill_color = 'white'
        self._items['polygon'].outline_color = 'blue'
        self._items['polygon'].active_outline_color = 'orange'
        self._items['polygon'].outline_width = 2.0
        self._items['polygon'].active_outline_width = 5.0
        self._items['polygon'].hidden = False
        self._items['polygon'].draggable = True
        self._items['polygon'].show_selection = True

    def coords(self, coords):
        """ given new coords, modify the existing polygon """

        # TODO: This should be re-written to be a call to the GItem.coords()
        # TODO: (Canvas items should not be directly manipulated at this level.)
        self.gcanvas.canvas.coords(self._tag, coords)

