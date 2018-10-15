#
# Starting to work on a major refactor to separate out GItems from GObjects
# The GItems will manage the individual canvas items, and their properties
# GObjects will be built of GItems, so one GObject can be composed of multiple
# GItems.
#
# The GItems will set various tags, but all key/mouse bindings will be done
# in the GObject based off of those tags.

from .gitem import (
    GLineItem,
    GRectItem,
    GOvalItem,
    GBufferGateBody,
)

class GObject:
    '''
    A container for GItems. Can be added to a GCanvas.
    '''

    def __init__(self, initial_x, initial_y, name_tag=None):

        # Remember where I'm drawn on the canvas
        self._x = initial_x
        self._y = initial_y

        # Remember my GCanvas
        self.gcanvas = None

        # my primary name tag
        # TODO: if no name_tag is given, we need to generate a random unique tag name
        self._tag = name_tag

        # my canvas item - this will get set to something in the sub-class that inherits from me
        # TODO: this should go away when we finish the GItem, and we will keep track of a set of
        # TODO: GItems instead.
        self.canvas_item = None

        # TODO: IN-PROGRESS: Let's keep track of the GItems here.
        # TODO: Each GItem will have its own item-level name, so let's use a Dictionary
        # TODO: Key will be the GItem name, and value will be the actual object
        self._items = {}

        # Move to GItem?
        # this data is used to keep track of a canvas object being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # NOTE: selection will be done at the GObject level, but bindings at GItem level
        # my selection status (am I selected or not)
        self.selected = False

        # Move to GItem?
        # all fillable canvas items will use these colors
        self.fill_color = 'white'
        self.selected_fill_color = '#1111FF'

        # Move to GItem?
        # current line width and active line width (changes when zooming in/out to maintain proper ratio)
        self.outline_width = 2
        self.outline_color = 'blue'
        self.active_outline_width = 5
        self.active_outline_color = 'orange'

        # Move to GItem?
        # various properties
        self._selectable = True       # if the GObject can be selected or not
        self._highlightable = True    # if we highlight the GObject upon <Enter> / de-highlight upon <Leave>
        self._draggable = True        # if the GObject can be click-hold-Dragged
        self._clickable = True        # if the GObject can be clicked
        self._connectable = False     # if the GObject can be connected to another GObject

    @staticmethod
    def factory(a_class, *args, **kwargs):
        return a_class(*args, **kwargs)


    # as GItems will be tagged with the parent name tag, we can continue to scale in the same way (i think)
    def scale(self, x_offset, y_offset, x_scale, y_scale):
        ''' scale by scale factor x_scale and y_scale relative to point (x_offset, y_offset) '''

        # scale the canvas items associated with self._tag
        self.gcanvas.canvas.scale(self._tag, x_offset, y_offset, x_scale, y_scale)

        # in theory, we could scale at different rates horizontally vs vertically, but
        # line widths are constant accross the whole item, so we just pick the x_scale
        sf = x_scale

        # scale my outline and active_outline widths
        for gitem_name in self._items:
            gitem = self._items[gitem_name]
            current_width = gitem.outline_width
            current_activewidth = gitem.active_outline_width
            new_width = float(current_width) * sf
            new_activewidth = float(current_activewidth) * sf
            gitem.outline_width = new_width
            gitem.active_outline_width = new_activewidth
            #print(f"{sf} {gitem_name}({gitem.item}) new width {new_width} new active width {new_activewidth}")


    def add_mouse_bindings(self):
        # add bindings for selection toggle on/off using Command-Click
        self.gcanvas.canvas.tag_bind(self._tag + "_draggable", "<Command-ButtonPress-1>", self.on_command_button_press)

        # add bindings for click and hold to drag an object
        self.gcanvas.canvas.tag_bind(self._tag + "_draggable", "<ButtonPress-1>", self.on_button_press)
        self.gcanvas.canvas.tag_bind(self._tag + "_draggable", "<ButtonRelease-1>", self.on_button_release)
        self.gcanvas.canvas.tag_bind(self._tag + "_draggable", "<B1-Motion>", self.on_button_motion)

        # add bindings for highlighting upon <Enter> and <Leave> events
        self.gcanvas.canvas.tag_bind(self._tag + "activate_together", "<Enter>", self.on_enter)
        self.gcanvas.canvas.tag_bind(self._tag + "activate_together", "<Leave>", self.on_leave)

        # add binding to handle Selection virtual events from a selection box
        self.gcanvas.canvas.bind("<<Selection>>", self.on_selection_event, "+")

    def on_button_press(self, event):
        ''' Beginning drag of an object - record the item and its location '''
        self._drag_data["item"] = self.gcanvas.canvas.find_closest(event.x, event.y)[0]
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
        # So we move all canvas items tagged with self._tag
        #
        # We also want to move any items tagged as "selected" which may have been selected by the selection box
        # However, if self._tag is contained within the selected set, we dont want to move it twice, otherwise
        # we end up with it moving twice as far on the canvas
        #
        # We have 2 cases to consider:
        # Are we moving an item that is NOT selected?  If so, just move it.
        # Or Are we moving an item that IS selected? If so, then move all selected items along with it
        items_im_composed_of = self.gcanvas.canvas.find_withtag(self._tag)
        #print("DEBUG: self._tag={} items_im_composed_of={}".format(self._tag, items_im_composed_of))
        tags_on_1st_item = self.gcanvas.canvas.gettags(items_im_composed_of[0]) # just look at the 1st item

        # Since all items will have the "selected" tag, we only need to check the 1st one
        if "selected" in tags_on_1st_item:
            self.gcanvas.canvas.move("selected", delta_x, delta_y)
        else:
            self.gcanvas.canvas.move(self._tag, delta_x, delta_y)

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set("Dragging something...")

    def on_command_button_press(self, event):
        ''' handle Command-Click on a GObject '''

        # convert from screen coords to canvas coords
        canvas = event.widget
        x = canvas.canvasx(event.x)
        y = canvas.canvasy(event.y)
        clicked_item = self.gcanvas.canvas.find_closest(x, y)[0]

        if self.selectable:
            self.toggle_selected()
            print("Item ID {} --> Command-Clicked --> Selected? {}".format(clicked_item, self.selected))
            if (self.selected):
                self.set_selected()
            else:
                self.clear_selected()
        else:
            print("Item {} not selectable.".format(clicked_item))

    def set_selected(self):
        if self.selectable:
            self.selected = True
            self.gcanvas.canvas.itemconfigure(self._tag + "_draggable", fill=self.selected_fill_color)
            self.gcanvas.canvas.addtag_withtag("selected", self._tag)  # add "selected" tag to item

    def clear_selected(self):
        if self.selectable:
            self.selected = False
            self.gcanvas.canvas.itemconfigure(self._tag + "_draggable", fill=self.fill_color)
            self.gcanvas.canvas.dtag(self._tag, "selected") # delete/remove the "selected" tag

    def toggle_selected(self):
        if self.selectable:
            self.selected = not self.selected

    def on_selection_event(self, event):
        #print("Selection event triggered {}".format(self._tag))
        self.update_selection_status()

    def update_selection_status(self):
        # If any part of me is "selected", then make sure all items are selected so that they move together
        selected = False
        #print("My primary tag: {}".format(self._tag))
        # Find all item IDs that are tagged with primary name tag
        ids = self.gcanvas.canvas.find_withtag(self._tag)
        # Check to see if at least one has the "selected" tag
        for id in (ids):
            tags_on_id = self.gcanvas.canvas.gettags(id)
            if "selected" in tags_on_id:
                selected = True
                break # out of loop, as we've found an item that is tagged with "selected"
        if selected:
            # We've found at least 1 item that is selected, so let's make sure all items are selected
            self.set_selected()
        else:
            self.clear_selected()

    def on_enter(self, event):
        self.gcanvas.canvas.tag_raise(self._tag)
        self.gcanvas.canvas.itemconfigure(self.canvas_item, outline=self.active_outline_color, width=self.active_outline_width)

    def on_leave(self, event):
        self.gcanvas.canvas.itemconfigure(self.canvas_item, outline=self.outline_color, width=self.outline_width)

    def hide(self):
        self.gcanvas.canvas.itemconfigure(self.canvas_item, state="hidden")

    def show(self):
        self.gcanvas.canvas.itemconfigure(self.canvas_item, state="normal")

    # TODO: The make_draggable() and make_undraggable methods need to be re-done
    # TODO: They should affect a GObject-level toggle, rather than manipulate
    # TODO: the GItem property.  The GItem property should be renamed to something
    # TODO: like "allow_initiate_drag" as it indicates that a click/drag can be
    # TODO: initiated from itself, not whether the larger GObject can be dragged.
    def make_undraggable(self):
        ''' Make the GObject undraggable (immovable) across the canvas '''
        for i in self._items:
            print(f"Setting GItem {i} dragability to False")
            self._items[i].draggable = False

    def make_draggable(self):
        ''' Make the GObject draggable across the canvas '''
        for i in self._items:
            print(f"Setting GItem {i} dragability to True")
            self._items[i].draggable = True

    def set_outline_width(self, width):
        self.outline_width = width

    def set_active_outline_width(self, width):
        self.active_outline_width = width

    @property
    def selectable(self):
        return self._selectable

    @selectable.setter
    def selectable(self, value):
        self._selectable = bool(value)

    @property
    def highlightable(self):
        return self._highlightable

    @highlightable.setter
    def highlightable(self, value):
        self._highlightable = bool(value)

    @property
    def draggable(self):
        return self._draggable

    @draggable.setter
    def draggable(self, value):
        self._draggable = bool(value)

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


# TODO:
# TODO:
# TODO:
# TODO:
# TODO:
# TODO:
# TODO:
# TODO: All of the below GObjects need to be converted to use a set of GItems
# TODO: We need to figure out what a GItem will look like, and then call the
# TODO: appropriate method to add GItems to a GObject.
# TODO:
# TODO:
# TODO:
# TODO:
# TODO:
# TODO:

class GFoo(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        length = args[2]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        # attributes unique to the GFoo
        self.length = length

    def add(self):
        # we need to make a registration method, the same way we did for GObjects with GCanvas
        # but for now, let's just do this hard coded...

        self._items['line1'] = GLineItem(self.gcanvas, self._x, self._y, self.length, self._tag)
        self._items['line1'].add()
        self._items['line1'].hidden = False
        self._items['line1'].draggable = False

        self._items['line2'] = GLineItem(self.gcanvas, self._x, self._y + 4, self.length, self._tag)
        self._items['line2'].add()
        self._items['line2'].hidden = False
        self._items['line2'].draggable = False

        self._items['line3'] = GLineItem(self.gcanvas, self._x, self._y + 8, self.length, self._tag)
        self._items['line3'].add()
        self._items['line3'].hidden = False
        self._items['line3'].draggable = False

        self._items['line4'] = GLineItem(self.gcanvas, self._x, self._y + 12, self.length, self._tag)
        self._items['line4'].add()
        self._items['line4'].hidden = False
        self._items['line4'].draggable = False

        self._items['oval1'] = GOvalItem(self.gcanvas, self._x, self._y + 16, self.length, self.length, self._tag)
        self._items['oval1'].add()
        self._items['oval1'].hidden = False
        self._items['oval1'].draggable = True
        self._items['oval1'].selectable = True


class GBufferGate(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

    def add(self):

        self._items['output_line'] = GLineItem(self.gcanvas, self._x + 58, self._y + 28, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 68, self._y + 23, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False

        self._items['input_line1'] = GLineItem(self.gcanvas, self._x, self._y + 19, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 14, 10, 10, self._tag)
        self._items['input_dot1'].add()
        self._items['input_dot1'].hidden = False
        self._items['input_dot1'].draggable = False

        self._items['input_line2'] = GLineItem(self.gcanvas, self._x, self._y + 37, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 32, 10, 10, self._tag)
        self._items['input_dot2'].add()
        self._items['input_dot2'].hidden = False
        self._items['input_dot2'].draggable = False

        self._items['body'] = GBufferGateBody(self.gcanvas, self._x, self._y, self._tag)
        self._items['body'].add()
        self._items['body'].hidden = False
        self._items['body'].draggable = True


class GRect(GObject):
    ''' Draw Square or Rectangle on a GCanvas '''

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

        self._items['rect1'] = GRectItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['rect1'].add()
        self._items['rect1'].hidden = False
        self._items['rect1'].draggable = True


class GOval(GObject):
    ''' Draw Oval or Circle on a GCanvas '''

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

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = True


class GGraphPaper(GObject):
    ''' Draw Graph Paper '''

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        width = args[2]
        height = args[3]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self.width = width
        self.height = height
        self.bg_color = "#eeffee"

    def add(self):
        # Create the canvas items in a hidden state so that we can show them only when we want to
        # Draw the Graph Paper background rectangle using a greenish-white tint
        self.canvas_item = self.gcanvas.canvas.create_rectangle(self._x, self._y,
                                                        self._x + self.width,
                                                        self._y + self.height,
                                                        fill=self.bg_color,
                                                        outline=self.bg_color,
                                                        state='hidden',
                                                        tag=self._tag)

        # Draw the Graph Paper lines.  We draw all of the vertical lines, followed by all of the
        # horizontal lines.  Every 100 pixels (or every 10th line) we draw using a DARKER green, to
        # simulate the classic "Engineer's Graph Paper".

        # Creates all vertical lines
        for i in range(self._x, self._x + self.width, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.gcanvas.canvas.create_line([(i, self._x), (i, self._x + self.height)], fill=line_color, tag=self._tag)

        # Creates all horizontal lines
        for i in range(self._y, self._y + self.height, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.gcanvas.canvas.create_line([(self._y, i), (self._y + self.width, i)], fill=line_color, tag=self._tag)

        # TODO:  Note, we do not have the "activate_together" tag here, as is used on other GObjects. This
        # TODO:  is a temporary hack, as we use this GraphPaper as the background, and do not want the
        # TODO:  on_enter and on_leave events to apply.  We should create a method that allows us to
        # TODO:  make_highlightable() on any GObject, and then we can choose NOT to for this GObject.
        # TODO:  Or, better yet, we should make it a property that we can set to True or False.




