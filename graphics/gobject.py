import math

class GObject:
    """ The parent class for all objects that can be placed on a GCanvas """

    def __init__(self, initial_x, initial_y, name_tag=None):

        # Remember where I'm drawn on the canvas
        self.x = initial_x
        self.y = initial_y

        # Remember my GCanvas
        self.gcanvas = None

        # Remember the canvas that I'm drawn on
        self.canvas = None

        # my primary name tag
        # TOOD: if no name_tag is given, we need to generate a random tag name
        self.tag = name_tag

        # my canvas item - this will get set to something in the sub-class that inherits from me
        # TODO: This really needs to be made into a list of canvas items, as some of our GObjects
        # TODO: contain multiple items, and we have no way of hiding/showing them if we dont keep
        # TODO: track of all of them.  (Take a look at GGraphPaper below.)
        self.canvas_item = None

        # this data is used to keep track of a canvas object being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # my selection status (am I selected or not)
        self.selected = False

        # all fillable canvas items will use these colors
        self.fill_color = 'white'
        self.selected_fill_color = '#1111FF'

        # current line width and active line width (changes when zooming in/out to maintain proper ratio)
        self.outline_width = 2
        self.outline_color = 'blue'
        self.active_outline_width = 5
        self.active_outline_color = 'orange'

        # TODO: setup a property 'highlightable' which will control if the GObject's outline is highlighted
        # TODO: when the mouse pointer enters.  Other properties we should add include:
        # TODO: 'draggable', 'selectable', 'clickable', 'connectable', etc.

    # Tell the GObject what GCanvas to draw itself on
    def add_to(self, gcanvas):
        self.gcanvas = gcanvas
        self.canvas = gcanvas.canvas
        self.add()  # Now that we know what GCanvas to use, add the GObject's canvas item(s) to the canvas
        self.gcanvas.add(self.tag, self)  # Let the GCanvas know we exist
        self.show() # GObjects are hidden by default
        self.add_mouse_bindings()

    # scaling a GObject will involve scaling the canvas items, as well as adjusting line/active line widths
    def scale(self, sf):
        ''' scale by scale factor sf '''

        # We should also scale the GObjects themselves (here), but currently we are using a feature
        # of the canvas to scale all items simultaneously within the GCanvas class to simulate Zooming.
        # We need to consider how outline and active_outline widths would/should be scaled when we are
        # both Zooming and scaling an individual GObject at the same time.

        # Scale my outline and active_outline widths
        current_width = self.outline_width
        current_activewidth = self.active_outline_width
        new_width = float(current_width) * sf
        new_activewidth = float(current_activewidth) * sf
        self.canvas.itemconfigure(self.tag, width=new_width)
        self.canvas.itemconfigure(self.tag, activewidth=new_activewidth)
        self.outline_width = new_width
        self.active_outline_width = new_activewidth
        #print(f"{sf} {self.tag} new width {new_width} new active width {new_activewidth}")

    def add_mouse_bindings(self):
        # add bindings for selection toggle on/off using Command-Click
        self.canvas.tag_bind(self.tag + "dragable", "<Command-ButtonPress-1>", self.on_command_button_press)

        # add bindings for click and hold to drag an object
        self.canvas.tag_bind(self.tag + "dragable", "<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.tag + "dragable", "<ButtonRelease-1>", self.on_button_release)
        self.canvas.tag_bind(self.tag + "dragable", "<B1-Motion>", self.on_button_motion)

        # add bindings for highlighting upon <Enter> and <Leave> events
        self.canvas.tag_bind(self.tag + "activate_together", "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag + "activate_together", "<Leave>", self.on_leave)

        # add binding to handle Selection virtual events from a selection box
        self.canvas.bind("<<Selection>>", self.on_selection_event, "+")

    def on_button_press(self, event):
        ''' Beginning drag of an object - record the item and its location '''
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_button_release(self, event):
        ''' End drag of an object - reset the drag information '''
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_button_motion(self, event):
        ''' Handle dragging of an object '''

        # This handler could be triggered by an accidental B1-Motion event while Command-Clicking to [de]select
        if self._drag_data["item"] is None:
            return

        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # We want to move all sub-objects/items, not just the one we grabbed with .find_closest()
        # So we move all canvas items tagged with self.tag
        #
        # We also want to move any items tagged as "selected" which may have been selected by the selection box
        # However, if self.tag is contained within the selected set, we dont want to move it twice, otherwise
        # we end up with it moving twice as far on the canvas
        #
        # We have 2 cases to consider:
        # Are we moving an item that is NOT selected?  If so, just move it.
        # Or Are we moving an item that IS selected? If so, then move all selected items along with it
        items_im_composed_of = self.canvas.find_withtag(self.tag)
        tags_on_1st_item = self.canvas.gettags(items_im_composed_of[0]) # just look at the 1st item

        # Since all items will have the "selected" tag, we only need to check the 1st one
        if "selected" in tags_on_1st_item:
            self.canvas.move("selected", delta_x, delta_y)
        else:
            self.canvas.move(self.tag, delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set("Dragging something...")

    def on_command_button_press(self, event):
        self.toggle_selected()
        #print("Command-Click, Selected? {}".format(self.selected))
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        if (self.selected):
            self.set_selected()
        else:
            self.clear_selected()

    def set_selected(self):
        self.selected = True
        self.canvas.itemconfigure(self.tag + "dragable", fill=self.selected_fill_color)
        self.canvas.addtag_withtag("selected", self.tag)

    def clear_selected(self):
        self.selected = False
        self.canvas.itemconfigure(self.tag + "dragable", fill=self.fill_color)
        self.canvas.dtag(self.tag, "selected") # delete/remove the "selected" tag

    def toggle_selected(self):
        self.selected = not self.selected

    def on_selection_event(self, event):
        #print("Selection event triggered {}".format(self.tag))
        self.update_selection_status()

    def update_selection_status(self):
        # If any part of me is "selected", then make sure all items are selected so that they move together
        selected = False
        #print("My primary tag: {}".format(self.tag))
        # Find all item IDs that are tagged with primary name tag
        ids = self.canvas.find_withtag(self.tag)
        # Check to see if at least one has the "selected" tag
        for id in (ids):
            tags_on_id = self.canvas.gettags(id)
            if "selected" in tags_on_id:
                selected = True
                break # out of loop, as we've found an item that is tagged with "selected"
        if selected:
            # We've found at least 1 item that is selected, so let's make sure all items are selected
            self.set_selected()
        else:
            self.clear_selected()

    def on_enter(self, event):
        self.canvas.tag_raise(self.tag)
        #active_outline_width = self.canvas.itemcget("scale_on_zoom_2_5", "activewidth")
        self.canvas.itemconfigure(self.canvas_item, outline=self.active_outline_color, width=self.active_outline_width)

    def on_leave(self, event):
        #outline_width = self.canvas.itemcget("scale_on_zoom_2_5", "width")
        self.canvas.itemconfigure(self.canvas_item, outline=self.outline_color, width=self.outline_width)

    def hide(self):
        self.canvas.itemconfigure(self.canvas_item, state="hidden")

    def show(self):
        self.canvas.itemconfigure(self.canvas_item, state="normal")

    def make_draggable(self):
        # Tag the canvas items as "dragable" so that we can drag them around the canvas
        self.canvas.addtag_withtag(self.tag + "dragable", self.canvas_item)

    def set_outline_width(self, width):
        self.outline_width = width

    def set_active_outline_width(self, width):
        self.active_outline_width = width


class BufferGate(GObject):
    ''' The Buffer Gate draws itself on a GCanvas '''

    def __init__(self, initial_x, initial_y, name_tag=None):

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

    def add(self):
        points = []
        points.extend((self.x, self.y))              # first point in polygon
        points.extend((self.x + 58, self.y + 28))
        points.extend((self.x +  0, self.y + 56))

        self.canvas_item = self.canvas.create_polygon(points,
                                                      outline=self.outline_color,
                                                      activeoutline=self.active_outline_color,
                                                      fill=self.fill_color,
                                                      width=self.outline_width,
                                                      activewidth=self.active_outline_width,
                                                      state='hidden',
                                                      tags=self.tag)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)


class GRect(GObject):
    ''' Draw Square or Rectangle on a GCanvas '''

    def __init__(self, initial_x, initial_y, width, height, name_tag=None):

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self.tag = name_tag
        self.width = width
        self.height = height

    def add(self):
        self.canvas_item = self.canvas.create_rectangle(self.x, self.y,
                                                        self.x + self.width, self.y + self.height,
                                                        outline=self.outline_color,
                                                        activeoutline=self.active_outline_color,
                                                        fill=self.fill_color,
                                                        width=self.outline_width,
                                                        activewidth=self.active_outline_width,
                                                        state='hidden',
                                                        tags=self.tag)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)


class GOval(GObject):
    ''' Draw Oval or Circle on a GCanvas '''

    def __init__(self, initial_x, initial_y, width, height, name_tag=None):

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self.tag = name_tag
        self.width = width
        self.height = height

    def add(self):
        # Create the canvas item in a hidden state so that we can show it only when we want to
        self.canvas_item = self.canvas.create_oval(self.x, self.y,
                                                   self.x + self.width, self.y + self.height,
                                                   outline=self.outline_color,
                                                   activeoutline=self.active_outline_color,
                                                   fill=self.fill_color,
                                                   width=self.outline_width,
                                                   activewidth=self.active_outline_width,
                                                   state='hidden',
                                                   tags=self.tag)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)



class GGraphPaper(GObject):
    ''' Draw Graph Paper '''

    def __init__(self, initial_x, initial_y, width, height, name_tag=None):

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self.tag = name_tag
        self.width = width
        self.height = height
        self.bg_color = "#eeffee"

    def add(self):
        # Create the canvas items in a hidden state so that we can show it only when we want to
        # Draw and tag a background rectangle which will give us the ability to scroll the canvas only when
        # clicking and dragging on the background, but will not drag when we click on another object on the
        # canvas (such as a gate or wire) as those objects will be tagged with different names. We bind the
        # tag of the background objects to the click/drag events.  See below scroll_start() and scroll_move()

        self.canvas_item = self.canvas.create_rectangle(self.x, self.y,
                                                        self.x + self.width,
                                                        self.y + self.height,
                                                        fill=self.bg_color,
                                                        outline=self.bg_color,
                                                        state='hidden',
                                                        tag=self.tag)

        # Draw the Graph Paper background.  We draw all of the vertical lines, followed by all of the
        # horizontal lines.  Every 100 pixels (or every 10th line) we draw using a DARKER green, to
        # simulate the classic "Engineer's Graph Paper".

        # Creates all vertical lines
        for i in range(self.x, self.x + self.width, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.canvas.create_line([(i, self.x), (i, self.x + self.height)], fill=line_color, tag=self.tag)

        # Creates all horizontal lines
        for i in range(self.y, self.y + self.height, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.canvas.create_line([(self.y, i), (self.y + self.width, i)], fill=line_color, tag=self.tag)


