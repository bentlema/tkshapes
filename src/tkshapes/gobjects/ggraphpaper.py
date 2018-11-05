
from ..gobject import GObject
from ..gitem import GLineItem, GRectItem


class GGraphPaper(GObject):
    """ Draw Graph Paper """

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        width = args[2]
        height = args[3]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._width = width
        self._height = height
        self._bg_color = "#eeffee"

    def add(self):
        # Draw the Graph Paper background rectangle using a greenish-white tint
        self._items['background_rect'] = GRectItem(
            self.gcanvas, self._x, self._y, self._x + self._width, self._y + self._height, self._tag)
        self._items['background_rect'].add()
        self._items['background_rect'].fill_color = self._bg_color
        self._items['background_rect'].outline_color = self._bg_color
        self._items['background_rect'].hidden = False
        self._items['background_rect'].raisable = False
        self._items['background_rect'].draggable = False
        self._items['background_rect'].selectable = False

        # Draw the Graph Paper lines.  We draw all of the vertical lines, followed by all of the
        # horizontal lines.  Every 100 pixels (or every 10th line) we draw using a DARKER green, to
        # simulate the classic "Engineer's Graph Paper".

        # Creates all vertical lines
        for i in range(self._x, self._x + self._width, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            points = [(i, self._x), (i, self._x + self._height)]
            self._items['graph_paper_vline'+str(i)] = GLineItem(self.gcanvas, points, self._tag)
            self._items['graph_paper_vline'+str(i)].add()
            self._items['graph_paper_vline'+str(i)].fill_color = line_color
            self._items['graph_paper_vline'+str(i)].outline_width = 1.0
            self._items['graph_paper_vline'+str(i)].active_outline_width = 1.0
            self._items['graph_paper_vline'+str(i)].hidden = False
            self._items['graph_paper_vline'+str(i)].raisable = False
            self._items['graph_paper_vline'+str(i)].draggable = False
            self._items['graph_paper_vline'+str(i)].selectable = False

        # Creates all horizontal lines
        for i in range(self._y, self._y + self._height, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            points = [(self._y, i), (self._y + self._width, i)]
            self._items['graph_paper_hline'+str(i)] = GLineItem(self.gcanvas, points, self._tag)
            self._items['graph_paper_hline'+str(i)].add()
            self._items['graph_paper_hline'+str(i)].fill_color = line_color
            self._items['graph_paper_hline'+str(i)].outline_width = 1.0
            self._items['graph_paper_hline'+str(i)].active_outline_width = 1.0
            self._items['graph_paper_hline'+str(i)].hidden = False
            self._items['graph_paper_hline'+str(i)].raisable = False
            self._items['graph_paper_hline'+str(i)].draggable = False
            self._items['graph_paper_hline'+str(i)].selectable = False

