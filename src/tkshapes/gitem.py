
class GItem:
    """
    A wrapper around a single canvas item
    """

    def __init__(self, gcanvas, initial_x, initial_y, name_tag=None):

        # Remember where I'm drawn on the canvas
        self._x = initial_x
        self._y = initial_y

        # Remember my GCanvas -- injected at object-creation time
        self._gcanvas = gcanvas

        # my primary name tag -- inherited from the parent GObject
        self._tag = name_tag

        # I should keep track of my owning GObject in case I want to refer back to its properties
        # but it'd need to pass that info in when I create the GItem (this is not used yet)
        self._owner = None

        # my canvas item - this will get set to something in the sub-class that inherits from me
        # Each GItem manages a SINGLE canvas item, but a GObject can own multiple GItems
        self._canvas_item = None

        # if I'm hidden or not
        self._hidden = True               # controlled by self.hidden property
        self._item_state = 'hidden'       # defaults to 'hidden', but will change according to self.hidden property

        # if I'm selected or not
        self._selected = False            # controlled by self.selected property

        # all fillable canvas items will use these colors by default
        self._fill_color = 'white'
        self._selected_fill_color = '#1111FF'

        # will reflect either fill_color or selected_fill_color depending on selection status
        self._current_fill_color = 'red'

        # current line width and active line width (changes when zooming in/out to maintain proper ratio)
        self._outline_width = 2
        self._outline_color = 'blue'
        self._active_outline_width = 5
        self._active_outline_color = 'orange'

        # if I'm highlighted or not, and a string identifying my highlight group
        self._highlighted = False
        self._highlight_group = None

        # various properties
        self._show_selection = True           # if the GItem changes color when selected
        self._show_highlight = True           # if the GItem shows when it is "active" or not
        self._draggable = True                # if the GItem can be click-Dragged
        self._clickable = True                # if the GItem can be clicked
        self._highlightable = True            # if the GItem is highlightable (only GItems with "outline" are)
        self._raisable = True                 # if the GItem should be raised upon <Enter> event
        self._always_on_top = False           # if the GItem should always be raised to the top upon <Enter> of any
        self._connectable_initiator = False   # if the GItem can be the initiator of a connector
        self._connectable_terminator = False  # if the GItem can be the termination point of a connector

    def hide(self):
        # Setting my own property
        self.hidden = True

    def show(self):
        # Setting my own property
        self.hidden = False

    def redraw(self):
        pass

    def raise_up(self):
        self._gcanvas.canvas.tag_raise(self._canvas_item)

    def center_point(self):
        """ return center point of the GItem based on bbox """
        bbox = self._gcanvas.canvas.bbox(self._canvas_item)
        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[2]
        y2 = bbox[3]
        bbox_x = x2 - x1
        bbox_y = y2 - y1
        mid_x = x1 + (bbox_x // 2)
        mid_y = y1 + (bbox_y // 2)
        return (mid_x, mid_y)

    @property
    def highlighted(self):
        return self._highlighted

    @highlighted.setter
    def highlighted(self, value):
        self._highlighted = bool(value)
        if value:
            self._gcanvas.canvas.itemconfigure(
                self._canvas_item,
                outline=self.active_outline_color,
                width=self.active_outline_width)
        else:
            self._gcanvas.canvas.itemconfigure(
                self._canvas_item,
                outline=self.outline_color,
                width=self.outline_width)

    @property
    def highlight_group(self):
        return self._highlight_group

    @highlight_group.setter
    def highlight_group(self, name):
        self._highlight_group = name
        # we dont need to add the tag, as we are moving away from this rogue communication path
        #print(f"Adding {name} tag to {self._canvas_item}")
        #self._gcanvas.canvas.addtag_withtag("highlight_group:" + name, self._canvas_item)

    @property
    def item(self):
        return self._canvas_item

    @property
    def item_state(self):
        return self._item_state

    @property
    def hidden(self):
        return self._hidden

    @hidden.setter
    def hidden(self, value):

        # if not hidden and we are setting to hidden
        if not self._hidden and value:
            self._gcanvas.canvas.itemconfigure(self._canvas_item, state="hidden")
            self._item_state = 'hidden'

        # if hidden and we are setting to not hidden
        if self._hidden and not value:
            self._gcanvas.canvas.itemconfigure(self._canvas_item, state="normal")
            self._item_state = 'normal'

        # set property to new value
        self._hidden = bool(value)

    @property
    def outline_color(self):
        return self._outline_color

    @outline_color.setter
    def outline_color(self, value):
        self._outline_color = value
        if self._canvas_item:
            if self._gcanvas.canvas.type(self._canvas_item) == 'line':
                self._gcanvas.canvas.itemconfigure(self._canvas_item, fill=value)
            else:
                self._gcanvas.canvas.itemconfigure(self._canvas_item, outline=value)

    @property
    def active_outline_color(self):
        return self._active_outline_color

    @active_outline_color.setter
    def active_outline_color(self, value):
        self._active_outline_color = value
        if self._canvas_item:
            if self._gcanvas.canvas.type(self._canvas_item) == 'line':
                self._gcanvas.canvas.itemconfigure(self._canvas_item, fill=value)
            else:
                self._gcanvas.canvas.itemconfigure(self._canvas_item, activeoutline=value)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected = bool(value)

        if value:
            self._gcanvas.canvas.addtag_withtag("selected", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, "selected")

        if self.show_selection:
            if value:
                self.current_fill_color = self.selected_fill_color
            else:
                self.current_fill_color = self.fill_color

    @property
    def current_fill_color(self):
        return self._current_fill_color

    @current_fill_color.setter
    def current_fill_color(self, value):
        self._current_fill_color = value
        if self._canvas_item:
            self._gcanvas.canvas.itemconfigure(self._canvas_item, fill=value)

    @property
    def fill_color(self):
        return self._fill_color

    @fill_color.setter
    def fill_color(self, value):
        self._fill_color = value
        self.current_fill_color = self.fill_color

    @property
    def selected_fill_color(self):
        return self._selected_fill_color

    @selected_fill_color.setter
    def selected_fill_color(self, value):
        self._selected_fill_color = value

    @property
    def outline_width(self):
        return self._outline_width

    @outline_width.setter
    def outline_width(self, value):
        self._outline_width = value
        if self._canvas_item:
            self._gcanvas.canvas.itemconfigure(self._canvas_item, width=value)

    @property
    def active_outline_width(self):
        return self._active_outline_width

    @active_outline_width.setter
    def active_outline_width(self, value):
        self._active_outline_width = value
        if self._canvas_item:
            self._gcanvas.canvas.itemconfigure(self._canvas_item, activewidth=value)

    @property
    def show_selection(self):
        return self._show_selection

    @show_selection.setter
    def show_selection(self, value):
        self._show_selection = bool(value)

    @property
    def show_highlight(self):
        return self._show_highlight

    @show_highlight.setter
    def show_highlight(self, value):
        self._show_highlight = bool(value)
        # Setting show_highlight to False implies the outline_width == active_outline_width
        if value is False:
            self.active_outline_width = self.outline_width

    @property
    def draggable(self):
        return self._draggable

    @draggable.setter
    def draggable(self, value):
        """ Tag the canvas item as "draggable" so that we can initiate a click-drag from it """
        self._draggable = bool(value)
        if value:
            self._gcanvas.canvas.addtag_withtag(self._tag + ":draggable", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, self._tag + ":draggable")

    @property
    def clickable(self):
        return self._clickable

    @clickable.setter
    def clickable(self, value):
        self._clickable = bool(value)

    @property
    def connectable_initiator(self):
        return self._connectable_initiator

    @connectable_initiator.setter
    def connectable_initiator(self, value):
        self._connectable_initiator = bool(value)
        if value:
            self._gcanvas.canvas.addtag_withtag(self._tag + ":connectable_initiator", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, self._tag + ":connectable_initiator")

    @property
    def connectable_terminator(self):
        return self._connectable_terminator

    @connectable_terminator.setter
    def connectable_terminator(self, value):
        self._connectable_terminator = bool(value)
        if value:
            self._gcanvas.canvas.addtag_withtag(self._tag + ":connectable_terminator", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, self._tag + ":connectable_terminator")

    @property
    def raisable(self):
        return self._raisable

    @raisable.setter
    def raisable(self, value):
        """ Tag the canvas items as "raisable" so they will raise up when entered """
        self._raisable = bool(value)
        if value:
            #print(f"Setting 'raisable' on canvas item {self._canvas_item}")
            self._gcanvas.canvas.addtag_withtag("raisable", self._canvas_item)
        else:
            #print(f"Deleting 'raisable' on canvas item {self._canvas_item}")
            self._gcanvas.canvas.dtag(self._canvas_item, "raisable")

    @property
    def always_on_top(self):
        return self._always_on_top

    @always_on_top.setter
    def always_on_top(self, value):
        """ Tag the canvas items as "always_on_top" so they will raise up when entered """
        self._always_on_top = bool(value)
        if value:
            #print(f"Setting 'always_on_top' on canvas item {self._canvas_item}")
            self._gcanvas.canvas.addtag_withtag("always_on_top", self._canvas_item)
        else:
            #print(f"Deleting 'always_on_top' on canvas item {self._canvas_item}")
            self._gcanvas.canvas.dtag(self._canvas_item, "always_on_top")

    @property
    def highlightable(self):
        return self._highlightable

    @highlightable.setter
    def highlightable(self, value):
        self._highlightable = bool(value)
        if value:
            self._gcanvas.canvas.addtag_withtag("highlightable", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, "highlightable")


class GHorzLineItem(GItem):
    """ Single-segment Horizontal line draws itself on a GCanvas """

    def __init__(self, gcanvas, initial_x, initial_y, length, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        # initialize properties
        self.outline_width = 2.0
        self.show_selection = False
        self.show_highlight = False

        # attributes unique to the GLine
        self.length = length
        self.coords = [(self._x, self._y), (self._x + self.length, self._y)]

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self.outline_width,
            activewidth=self.outline_width,
            state=self._item_state,
            tags=self._tag)

        # the item should NOT be raisable by default unless overridden in the GObject
        self.raisable = False
        self.highlightable = False


class GVertLineItem(GItem):
    """ Single-segment Vertical line draws itself on a GCanvas """

    def __init__(self, gcanvas, initial_x, initial_y, length, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        # initialize properties
        self.outline_width = 2.0
        self.show_selection = False
        self.show_highlight = False

        # attributes unique to the GLine
        self.length = length
        self.coords = [(self._x, self._y), (self._x, self._y + self.length)]

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self.outline_width,
            activewidth=self.outline_width,
            state=self._item_state,
            tags=self._tag)

        # the item should NOT be raisable by default unless overridden in the GObject
        self.raisable = False
        self.highlightable = False

class GLineItem(GItem):
    """ Multi-segment line defined by list of points draws itself on a GCanvas """

    def __init__(self, gcanvas, points, name_tag=None):
        initial_x, initial_y = points[0]
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self.coords = points

        # initialize properties
        self.outline_width = 2.0
        self.show_selection = False
        self.show_highlight = False

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self.outline_width,
            activewidth=self.outline_width,
            state=self._item_state,
            tags=self._tag)

        # the item should NOT be raisable by default unless overridden in the GObject
        self.raisable = False
        self.highlightable = False

class GWireItem(GItem):
    """ Multi-segment Wire defined by list of points draws itself on a GCanvas """

    def __init__(self, gcanvas, points, name_tag=None):
        #initial_x, initial_y = points[0]
        super().__init__(gcanvas, 0, 0, name_tag)

        self.coords = points

        # initialize properties
        self.outline_width = 2.0
        self.show_selection = False
        self.show_highlight = False

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self.outline_width,
            activewidth=self.outline_width,
            state=self._item_state,
            capstyle="round", smooth=True, splinesteps=20,
            tags=self._tag)

        # the item should NOT be raisable by default unless overridden in the GObject
        self.raisable = False
        self.highlightable = False

    def redraw(self):
        self._gcanvas.canvas.coords(self._canvas_item, self.coords)


class GRectItem(GItem):
    """ Draw Square or Rectangle on a GCanvas """

    def __init__(self, gcanvas, initial_x, initial_y, width, height, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self.width = width
        self.height = height

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_rectangle(
            self._x, self._y,
            self._x + self.width, self._y + self.height,
            outline=self._outline_color,
            activeoutline=self._outline_color,
            fill=self.fill_color,            # property
            width=self.outline_width,        # property
            activewidth=self.outline_width,  # property
            state=self._item_state,
            tags=self._tag)

        # the item should be raisable by default unless overridden in the GObject
        self.raisable = True

        # Tag the specific canvas items we want to activate (highlight) together
        #self._gcanvas.canvas.addtag_withtag(self._tag + "activate_together", self._canvas_item)
        self.highlightable = True


class GOvalItem(GItem):
    """ Draw Oval or Circle on a GCanvas """

    def __init__(self, gcanvas, initial_x, initial_y, width, height, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self.width = width
        self.height = height

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_oval(
            self._x, self._y,
            self._x + self.width, self._y + self.height,
            outline=self._outline_color,
            activeoutline=self._outline_color,
            fill=self.fill_color,            # property
            width=self.outline_width,        # property
            activewidth=self.outline_width,  # property
            state=self._item_state,
            tags=self._tag)

        # the item should be raisable by default unless overridden in the GObject
        self.raisable = True

        # Tag the specific canvas items we want to activate (highlight) together
        #self._gcanvas.canvas.addtag_withtag(self._tag + "activate_together", self._canvas_item)
        self.highlightable = True


class GPolygonItem(GItem):
    """ Draw Polygon on a GCanvas """

    def __init__(self, gcanvas, points, name_tag=None):

        initial_x = points[0]
        initial_y = points[1]

        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self._points = points

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_polygon(
            self._points,
            outline=self._outline_color,
            activeoutline=self._outline_color,
            fill=self.fill_color,            # property
            width=self.outline_width,        # property
            activewidth=self.outline_width,  # property
            state=self._item_state,
            tags=self._tag)

        # the item should be raisable by default unless overridden in the GObject
        self.raisable = True

        # Tag the specific canvas items we want to activate (highlight) together
        self.highlightable = True

