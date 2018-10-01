import math

class GObject:
    """ The parent class for all objects that can be placed on a GCanvas """

    def __init__(self, gcanvas, name_tag, initial_x, initial_y):

        # Remember where I'm drawn on the canvas
        self.x = initial_x
        self.y = initial_y

        # Remember my GCanvas
        self.gcanvas = gcanvas

        # Remember the canvas that I'm drawn on
        self.canvas = gcanvas.canvas

        # my primary name tag
        self.tag = name_tag

        # my canvas item - this will get set to something in the sub-class that inherits from me
        self.canvas_item = None

        # this data is used to keep track of a canvas object being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # my selection status (am I selected or not)
        self.selected = False

        # add bindings for selection toggle on/off using Command-Click
        self.canvas.tag_bind(self.tag + "dragable", "<Command-ButtonPress-1>", self.on_command_button_press)

        # add bindings for click and hold to drag an object
        self.canvas.tag_bind(self.tag + "dragable", "<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.tag + "dragable", "<ButtonRelease-1>", self.on_button_release)
        self.canvas.tag_bind(self.tag + "dragable", "<B1-Motion>", self.on_button_motion)

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
        print("Command-Click, Selected? {}".format(self.selected))
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        if (self.selected):
            self.set_selected()
        else:
            self.clear_selected()

    def set_selected(self):
        self.selected = True
        self.canvas.itemconfigure(self.tag + "dragable", fill='#1111FF') # Bright Blue
        self.canvas.addtag_withtag("selected", self.tag)

    def clear_selected(self):
        self.selected = False
        self.canvas.itemconfigure(self.tag + "dragable", fill='white')
        self.canvas.dtag(self.tag, "selected") # delete/remove the "selected" tag

    def toggle_selected(self):
        self.selected = not self.selected

    def on_selection_event(self, event):
        print("Selection event triggered {}".format(self.tag))
        self.update_selection_status()

    def update_selection_status(self):
        # If any part of me is "selected", then make sure all items are selected so that they move together
        selected = False
        print("My primary tag: {}".format(self.tag))
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
        active_outline_width = self.canvas.itemcget("scale_on_zoom_2_5", "activewidth")
        self.canvas.itemconfigure(self.canvas_item, outline='orange', width=active_outline_width)

    def on_leave(self, event):
        outline_width = self.canvas.itemcget("scale_on_zoom_2_5", "width")
        self.canvas.itemconfigure(self.canvas_item, outline='blue', width=outline_width)


class BufferGate(GObject):
    """The Buffer Gate draws itself on a canvas"""

    def __init__(self, gcanvas, name_tag, initial_x, initial_y):

        # Initialize parent GObject class
        super().__init__(gcanvas, name_tag, initial_x, initial_y)

        points = []
        points.extend((self.x, self.y))              # first point in polygon
        points.extend((self.x + 58, self.y + 28))
        points.extend((self.x +  0, self.y + 56))

        self.canvas_item = self.canvas.create_polygon(points,
                                               outline='blue',
                                               activeoutline='orange',
                                               fill='white',
                                               width=2,
                                               activewidth=5,
                                               tags=name_tag)

        self.canvas.addtag_withtag("scale_on_zoom_2_5", self.canvas_item)
        self.canvas.addtag_withtag(self.tag + "dragable", self.canvas_item)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)

        # add bindings for highlighting upon <Enter> and <Leave> events
        self.canvas.tag_bind(self.tag + "activate_together", "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag + "activate_together", "<Leave>", self.on_leave)

        # add bindings for selection - must be done for every gate, as this type of binding
        # does not work when inheriting from the parent class
        self.canvas.bind("<<Selection>>", self.on_selection_event, "+")



class GRect(GObject):
    ''' Draw rectangle on a canvas '''

    def __init__(self, gcanvas, name_tag, initial_x, initial_y, width, height):

        # Initialize parent GObject class
        super().__init__(gcanvas, name_tag, initial_x, initial_y)

        self.canvas_item = self.canvas.create_rectangle(self.x, self.y, self.x + width, self.y + height,
                                               outline='blue',
                                               activeoutline='orange',
                                               fill='white',
                                               width=2,
                                               activewidth=5,
                                               tags=name_tag)

        self.canvas.addtag_withtag("scale_on_zoom_2_5", self.canvas_item)
        self.canvas.addtag_withtag(self.tag + "dragable", self.canvas_item)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)

        # add bindings for highlighting upon <Enter> and <Leave> events
        self.canvas.tag_bind(self.tag + "activate_together", "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag + "activate_together", "<Leave>", self.on_leave)

        # add bindings for selection - must be done for every gate, as this type of binding
        # does not work when inheriting from the parent class
        self.canvas.bind("<<Selection>>", self.on_selection_event, "+")








class GOval(GObject):
    ''' Draw circle on a canvas '''

    def __init__(self, gcanvas, name_tag, initial_x, initial_y, width, height):

        # Initialize parent GObject class
        super().__init__(gcanvas, name_tag, initial_x, initial_y)

        self.canvas_item = self.canvas.create_oval(self.x, self.y, self.x + width, self.y + height,
                                                        outline='blue',
                                                        activeoutline='orange',
                                                        fill='white',
                                                        width=2,
                                                        activewidth=5,
                                                        tags=name_tag)

        self.canvas.addtag_withtag("scale_on_zoom_2_5", self.canvas_item)
        self.canvas.addtag_withtag(self.tag + "dragable", self.canvas_item)

        # Tag the specific canvas items we want to activate (highlight) together
        self.canvas.addtag_withtag(self.tag + "activate_together", self.canvas_item)

        # add bindings for highlighting upon <Enter> and <Leave> events
        self.canvas.tag_bind(self.tag + "activate_together", "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag + "activate_together", "<Leave>", self.on_leave)

        # add bindings for selection - must be done for every gate, as this type of binding
        # does not work when inheriting from the parent class
        self.canvas.bind("<<Selection>>", self.on_selection_event, "+")
