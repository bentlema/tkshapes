
class GItem:
    '''
    A wrapper around a single canvas item
    '''

    def __init__(self, gcanvas, initial_x, initial_y, name_tag=None):

        # Remember where I'm drawn on the canvas
        self._x = initial_x
        self._y = initial_y

        # Remember my GCanvas -- injected at object-creation time
        self._gcanvas = gcanvas

        # my primary name tag -- inherited from the parent GObject
        self._tag = name_tag

        # my canvas item - this will get set to something in the sub-class that inherits from me
        # Each GItem manages a SINGLE canvas item, but a GObject can own multiple GItems
        self._canvas_item = None

        # if I'm hidden or not
        self._hidden = True               # controlled by self.hidden property
        self._item_state = 'hidden'       # defaults to 'hidden', but will change according to self.hidden property

        # all fillable canvas items will use these colors
        self._fill_color = 'white'
        self._selected_fill_color = '#1111FF'

        # current line width and active line width (changes when zooming in/out to maintain proper ratio)
        self._outline_width = 2
        self._outline_color = 'blue'
        self._active_outline_width = 5
        self._active_outline_color = 'orange'

        # various properties
        self._show_selection = True       # if the GItem changes color when selected
        self._show_highlight = True       # if the GItem shows when it is "active" or not
        self._draggable = True            # if the GItem can be click-Dragged
        self._clickable = True            # if the GItem can be clicked
        self._connectable = False         # if the GItem can be connected to another GItem

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

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
        ''' Tag the canvas items as "draggable" so that we can drag them around the canvas '''
        self._draggable = bool(value)
        if value:
            self._gcanvas.canvas.addtag_withtag(self._tag + "_draggable", self._canvas_item)
        else:
            self._gcanvas.canvas.dtag(self._canvas_item, self._tag + "_draggable")

    @property
    def clickable(self):
        return self._clickable

    @clickable.setter
    def clickable(self, value):
        self._clickable = bool(value)

    @property
    def connectable(self):
        return self._connectable

    @connectable.setter
    def connectable(self, value):
        self._connectable = bool(value)


class GLineItem(GItem):
    ''' Basic straight line draws itself on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, length, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        # by default, the line will not display its selection or highlight state
        self.outline_width = 2.0
        self.show_selection = False
        self.show_highlight = False

        # attributes unique to the GLine
        self.length = length

        # TODO: need to implement angle, and also the ability to specify two points, rather than length
        # TODO: we should convert to using kwargs so we can pass in alternate specifications
        self.angle = 0

        self.coords = [(self._x, self._y), (self._x + self.length, self._y)]

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self.outline_width,
            activewidth=self.active_outline_width,
            state=self._item_state,
            tags=self._tag)


class GBufferGateBody(GItem):
    ''' The Buffer Gate Triangle draws itself on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

    def add(self):
        # Draw the triangle portion of the BufferGate
        points = []
        points.extend((self._x, self._y))              # first point in polygon
        points.extend((self._x + 58, self._y + 28))
        points.extend((self._x +  0, self._y + 56))

        self._canvas_item = self._gcanvas.canvas.create_polygon(
            points,
            outline=self._outline_color,
            activeoutline=self._active_outline_color,
            fill=self._fill_color,
            width=self.outline_width,
            activewidth=self.active_outline_width,
            state=self._item_state,
            tags=self._tag)

        # will leave this here for now, but I think I'll come up with a differet/better way to control highlight groups
        # Tag the specific canvas items we want to activate (highlight) together
        self._gcanvas.canvas.addtag_withtag(self._tag + "activate_together", self._canvas_item)


class GRectItem(GItem):
    ''' Draw Square or Rectangle on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, width, height, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self.width = width
        self.height = height

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_rectangle(
            self._x, self._y,
            self._x + self.width, self._y + self.height,
            outline=self._outline_color,
            activeoutline=self._active_outline_color,
            fill=self._fill_color,
            width=self._outline_width,
            activewidth=self._active_outline_width,
            state=self._item_state,
            tags=self._tag)

        # Tag the specific canvas items we want to activate (highlight) together
        self._gcanvas.canvas.addtag_withtag(self._tag + "activate_together", self._canvas_item)


class GOvalItem(GItem):
    ''' Draw Oval or Circle on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, width, height, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        self.width = width
        self.height = height

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_oval(
            self._x, self._y,
            self._x + self.width, self._y + self.height,
            outline=self._outline_color,
            activeoutline=self._active_outline_color,
            fill=self._fill_color,
            width=self._outline_width,
            activewidth=self._active_outline_width,
            state=self._item_state,
            tags=self._tag)

        # Tag the specific canvas items we want to activate (highlight) together
        self._gcanvas.canvas.addtag_withtag(self._tag + "activate_together", self._canvas_item)


# Need to separate out the individual items
#class GGraphPaper(GItem):
#    ''' Draw Graph Paper '''
#
#    def __init__(self, initial_x, initial_y, width, height, name_tag=None):
#
#        super().__init__(initial_x, initial_y, name_tag)
#
#        self.tag = name_tag
#        self.width = width
#        self.height = height
#        self.bg_color = "#eeffee"
#
#    def add(self):
#        # Create the canvas items in a hidden state so that we can show them only when we want to
#        # Draw the Graph Paper background rectangle using a greenish-white tint
#        self.canvas_item = self.gcanvas.canvas.create_rectangle(self.x, self.y,
#                                                        self.x + self.width,
#                                                        self.y + self.height,
#                                                        fill=self.bg_color,
#                                                        outline=self.bg_color,
#                                                        state='hidden',
#                                                        tag=self.tag)
#
#        # Draw the Graph Paper lines.  We draw all of the vertical lines, followed by all of the
#        # horizontal lines.  Every 100 pixels (or every 10th line) we draw using a DARKER green, to
#        # simulate the classic "Engineer's Graph Paper".
#
#        # Creates all vertical lines
#        for i in range(self.x, self.x + self.width, 10):
#            if (i % 100) == 0:
#                line_color = "#aaffaa"
#            else:
#                line_color = "#ccffcc"
#            self.gcanvas.canvas.create_line([(i, self.x), (i, self.x + self.height)], fill=line_color, tag=self.tag)
#
#        # Creates all horizontal lines
#        for i in range(self.y, self.y + self.height, 10):
#            if (i % 100) == 0:
#                line_color = "#aaffaa"
#            else:
#                line_color = "#ccffcc"
#            self.gcanvas.canvas.create_line([(self.y, i), (self.y + self.width, i)], fill=line_color, tag=self.tag)
#
#        # TODO:  Note, we do not have the "activate_together" tag here, as is used on other GObjects. This
#        # TODO:  is a temporary hack, as we use this GraphPaper as the background, and do not want the
#        # TODO:  on_enter and on_leave events to apply.  We should create a method that allows us to
#        # TODO:  make_highlightable() on any GObject, and then we can choose NOT to for this GObject.
#        # TODO:  Or, better yet, we should make it a property that we can set to True or False.
#


