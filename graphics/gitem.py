
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

        # this data is used to keep track of a canvas object being dragged
        #self._drag_data = {"x": 0, "y": 0, "item": None}

        # individual items are not selected--that state is kept track of at the GObject level
        # my selection status (am I selected or not? only applies if is selectable)
        #self._selected = False

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

    # still trying to determine how we will do scaling.
    # if GItems contain the tag of the parent GObject, we can continue to do scaling at the GObject level,
    # which seems like the simplest thing to do... we shall see...
#    def scale(self, x_offset, y_offset, x_scale, y_scale):
#        ''' scale by scale factor x_scale and y_scale relative to point (x_offset, y_offset) '''
#        # We should also scale the GObjects themselves (here), but currently we are using a feature
#        # of the canvas to scale all items simultaneously within the GCanvas class to simulate Zooming.
#        # We need to consider how outline and active_outline widths would/should be scaled when we are
#        # both Zooming and scaling an individual GObject at the same time.
#        #
#        self.gcanvas.canvas.scale(self.tag, x_offset, y_offset, x_scale, y_scale)
#        self.scale_outline_width(x_scale)
#
#    def scale_outline_width(self, sf):
#        ''' scale outline width and active outline width by scale factor sf '''
#
#        # Scale my outline and active_outline widths
#        current_width = self.outline_width
#        current_activewidth = self.active_outline_width
#        new_width = float(current_width) * sf
#        new_activewidth = float(current_activewidth) * sf
#        self.gcanvas.canvas.itemconfigure(self.tag, width=new_width)
#        self.outline_width = new_width
#
#        # We adjust activewidth / active_outline_width ONLY if the GObject is highlightable
#        if self.highlightable:
#            self.gcanvas.canvas.itemconfigure(self.tag, activewidth=new_activewidth)
#            self.active_outline_width = new_activewidth

        #print(f"{sf} {self.tag} new width {new_width} new active width {new_activewidth}")

    # def add_mouse_bindings(self):
    #     # add bindings for selection toggle on/off using Command-Click
    #     self.gcanvas.canvas.tag_bind(self.tag + "draggable", "<Command-ButtonPress-1>", self.on_command_button_press)

        # # add bindings for click and hold to drag an object
        # self.gcanvas.canvas.tag_bind(self.tag + "draggable", "<ButtonPress-1>", self.on_button_press)
        # self.gcanvas.canvas.tag_bind(self.tag + "draggable", "<ButtonRelease-1>", self.on_button_release)
        # self.gcanvas.canvas.tag_bind(self.tag + "draggable", "<B1-Motion>", self.on_button_motion)

        # # add bindings for highlighting upon <Enter> and <Leave> events
        # self.gcanvas.canvas.tag_bind(self.tag + "activate_together", "<Enter>", self.on_enter)
        # self.gcanvas.canvas.tag_bind(self.tag + "activate_together", "<Leave>", self.on_leave)

        # # add binding to handle Selection virtual events from a selection box
        # self.gcanvas.canvas.bind("<<Selection>>", self.on_selection_event, "+")

    # def on_button_press(self, event):
    #     ''' Beginning drag of an object - record the item and its location '''
    #     self._drag_data["item"] = self.gcanvas.canvas.find_closest(event.x, event.y)[0]
    #     self._drag_data["x"] = event.x
    #     self._drag_data["y"] = event.y

    # def on_button_release(self, event):
    #     ''' End drag of an object - reset the drag information '''
    #     self._drag_data["item"] = None
    #     self._drag_data["x"] = 0
    #     self._drag_data["y"] = 0

    # def on_button_motion(self, event):
    #     ''' Handle dragging of an object '''

        # # This handler could be triggered by an accidental B1-Motion event while Command-Clicking to [de]select
        # if self._drag_data["item"] is None:
        #     return

        # # compute how much the mouse has moved
        # delta_x = event.x - self._drag_data["x"]
        # delta_y = event.y - self._drag_data["y"]

        # # We want to move all sub-objects/items, not just the one we grabbed with .find_closest()
        # # So we move all canvas items tagged with self.tag
        # #
        # # We also want to move any items tagged as "selected" which may have been selected by the selection box
        # # However, if self.tag is contained within the selected set, we dont want to move it twice, otherwise
        # # we end up with it moving twice as far on the canvas
        # #
        # # We have 2 cases to consider:
        # # Are we moving an item that is NOT selected?  If so, just move it.
        # # Or Are we moving an item that IS selected? If so, then move all selected items along with it
        # items_im_composed_of = self.gcanvas.canvas.find_withtag(self.tag)
        # #print("DEBUG: self.tag={} items_im_composed_of={}".format(self.tag, items_im_composed_of))
        # tags_on_1st_item = self.gcanvas.canvas.gettags(items_im_composed_of[0]) # just look at the 1st item

        # # Since all items will have the "selected" tag, we only need to check the 1st one
        # if "selected" in tags_on_1st_item:
        #     self.gcanvas.canvas.move("selected", delta_x, delta_y)
        # else:
        #     self.gcanvas.canvas.move(self.tag, delta_x, delta_y)

        # # record the new position
        # self._drag_data["x"] = event.x
        # self._drag_data["y"] = event.y

        # # update status var
        # if self.gcanvas.status_var:
        #     self.gcanvas.status_var.set("Dragging something...")

    # def on_command_button_press(self, event):
    #     ''' handle Command-Click on a GObject '''

        # # convert from screen coords to canvas coords
        # canvas = event.widget
        # x = canvas.canvasx(event.x)
        # y = canvas.canvasy(event.y)
        # clicked_item = self.gcanvas.canvas.find_closest(x, y)[0]

        # if self.selectable:
        #     self.toggle_selected()
        #     print("Item ID {} --> Command-Clicked --> Selected? {}".format(clicked_item, self.selected))
        #     if (self.selected):
        #         self.set_selected()
        #     else:
        #         self.clear_selected()
        # else:
        #     print("Item {} not selectable.".format(clicked_item))

    # def set_selected(self):
    #     if self.selectable:
    #         self.selected = True
    #         self.gcanvas.canvas.itemconfigure(self.tag + "draggable", fill=self.selected_fill_color)
    #         self.gcanvas.canvas.addtag_withtag("selected", self.tag)  # add "selected" tag to item

    # def clear_selected(self):
    #     if self.selectable:
    #         self.selected = False
    #         self.gcanvas.canvas.itemconfigure(self.tag + "draggable", fill=self.fill_color)
    #         self.gcanvas.canvas.dtag(self.tag, "selected") # delete/remove the "selected" tag

    # def toggle_selected(self):
    #     if self.selectable:
    #         self.selected = not self.selected

    # def on_selection_event(self, event):
    #     #print("Selection event triggered {}".format(self.tag))
    #     self.update_selection_status()

    # def update_selection_status(self):
    #     # If any part of me is "selected", then make sure all items are selected so that they move together
    #     selected = False
    #     #print("My primary tag: {}".format(self.tag))
    #     # Find all item IDs that are tagged with primary name tag
    #     ids = self.gcanvas.canvas.find_withtag(self.tag)
    #     # Check to see if at least one has the "selected" tag
    #     for id in (ids):
    #         tags_on_id = self.gcanvas.canvas.gettags(id)
    #         if "selected" in tags_on_id:
    #             selected = True
    #             break # out of loop, as we've found an item that is tagged with "selected"
    #     if selected:
    #         # We've found at least 1 item that is selected, so let's make sure all items are selected
    #         self.set_selected()
    #     else:
    #         self.clear_selected()

    # def on_enter(self, event):
    #     self.gcanvas.canvas.tag_raise(self.tag)
    #     self.gcanvas.canvas.itemconfigure(self.canvas_item, outline=self.active_outline_color, width=self.active_outline_width)

    # def on_leave(self, event):
    #     self.gcanvas.canvas.itemconfigure(self.canvas_item, outline=self.outline_color, width=self.outline_width)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    @property
    def item_state(self):
        return self._item_state

    # Let's not use this setter, and use the hidden.setter to control
    #@item_state.setter
    #def item_state(self, value):
    #    # should be 'normal', 'hidden', or 'disabled'
    #    self._item_state = str(value)

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
        self._outline_width = int(value)

    @property
    def active_outline_width(self):
        return self._active_outline_width

    @active_outline_width.setter
    def active_outline_width(self, value):
        self._active_outline_width = int(value)

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




class GLine(GItem):
    ''' Basic straight line draws itself on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, length, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        # by default, the line will not display its selection or highlight state
        self.show_selection = False
        self.show_highlight = False

        # attributes unique to the GLine
        self.length = length

        # TODO: need to implement angle, and also the ability to specify two points, rather than length
        # TODO: we should convert to using kwargs so we can pass in alternate specifications
        self.angle = 0

        self.coords = [ (self._x, self._y), (self._x + self.length, self._y)]

    def add(self):
        self._canvas_item = self._gcanvas.canvas.create_line(
            self.coords,
            fill=self._outline_color,
            width=self._outline_width,
            activewidth=self._outline_width,
            state=self._item_state,
            tags=self._tag)


#class GBufferGateBody(GItem):
#    ''' The Triangle draws itself on a GCanvas '''
#
#    def __init__(self, initial_x, initial_y, name_tag=None):
#
#        super().__init__(initial_x, initial_y, name_tag)
#
#    def add(self):
#        # Draw the triangle portion of the BufferGate
#        points = []
#        points.extend((self.x, self.y))              # first point in polygon
#        points.extend((self.x + 58, self.y + 28))
#        points.extend((self.x +  0, self.y + 56))
#
#        self.canvas_item = self.gcanvas.canvas.create_polygon(points,
#                                                      outline=self.outline_color,
#                                                      activeoutline=self.active_outline_color,
#                                                      fill=self.fill_color,
#                                                      width=self.outline_width,
#                                                      activewidth=self.active_outline_width,
#                                                      state='hidden',
#                                                      tags=self.tag)
#
#        # Tag the specific canvas items we want to activate (highlight) together
#        self.gcanvas.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)


#class GRect(GItem):
#    ''' Draw Square or Rectangle on a GCanvas '''
#
#    def __init__(self, initial_x, initial_y, width, height, name_tag=None):
#
#        super().__init__(initial_x, initial_y, name_tag)
#
#        self.tag = name_tag
#        self.width = width
#        self.height = height
#
#    def add(self):
#        self.canvas_item = self.gcanvas.canvas.create_rectangle(self.x, self.y,
#                                                        self.x + self.width, self.y + self.height,
#                                                        outline=self.outline_color,
#                                                        activeoutline=self.active_outline_color,
#                                                        fill=self.fill_color,
#                                                        width=self.outline_width,
#                                                        activewidth=self.active_outline_width,
#                                                        state='hidden',
#                                                        tags=self.tag)
#
#        # Tag the specific canvas items we want to activate (highlight) together
#        self.gcanvas.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)


class GOval(GItem):
    ''' Draw Oval or Circle on a GCanvas '''

    def __init__(self, gcanvas, initial_x, initial_y, width, height, name_tag=None):
        super().__init__(gcanvas, initial_x, initial_y, name_tag)

        # attributes unique to the GLine
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


#class GInputConnection:
#
#    def __init__(self, parent, starting_point, label):
#        self.label = label
#        self.parent = parent
#
#        (x, y) = starting_point
#
#        self.input_line = parent.canvas.create_line(x, y, x - 15, y,
#                                                    width=2,
#                                                    activewidth=2,
#                                                    fill="blue",
#                                                    activefill="blue",
#                                                    tag=parent.tag)
#
#        self.output_joint = parent.canvas.create_oval(x - 15, y - 6, x - 27, y + 6,
#                                                      width=2,
#                                                      activewidth=5,
#                                                      fill="white",
#                                                      outline="blue",
#                                                      activeoutline="orange",
#                                                      tag=parent.tag)



#class GOutputConnection:
#
#    def __init__(self, parent, starting_point, label):
#        self.label = label
#        self.parent = parent
#
#        (x0, y0) = starting_point
#        (x1, y1) = x0 + 10, y0
#
#        self.output_line = parent.canvas.create_line(x0, y0, x1, y1,
#                                                     width=2,
#                                                     activewidth=2,
#                                                     fill="blue",
#                                                     activefill="blue",
#                                                     tag=parent.tag)
#
#        self.output_joint = parent.canvas.create_oval(x1, y1 - 6, x1 + 12, y1 + 6,
#                                                      width=2,
#                                                      activewidth=5,
#                                                      fill="white",
#                                                      outline="blue",
#                                                      activeoutline="orange",
#                                                      tag=parent.tag)



#class GInvertedOutputConnection:
#
#    def __init__(self, parent, starting_point, label):
#        self.label = label
#        self.parent = parent
#
#        (x0, y0) = starting_point
#        (x1, y1) = x0 + 10, y0
#
#        self.output_line = parent.canvas.create_line(x0 + 8, y0, x1 + 8, y1,
#                                                     width=2,
#                                                     activewidth=2,
#                                                     fill="blue",
#                                                     activefill="blue",
#                                                     tag=parent.tag)
#
#        self.output_inverter = parent.canvas.create_oval(x0, y0 - 4, x0 + 8, y0 + 4,
#                                                         width=2,
#                                                         activewidth=5,
#                                                         fill="white",
#                                                         outline="blue",
#                                                         activeoutline="orange",
#                                                         tag=parent.tag)
#
#        self.output_joint = parent.canvas.create_oval(x1 + 8, y1 - 6, x1 + 20, y1 + 6,
#                                                      width=2,
#                                                      activewidth=5,
#                                                      fill="white",
#                                                      outline="blue",
#                                                      activeoutline="orange",
#                                                      tag=parent.tag)


