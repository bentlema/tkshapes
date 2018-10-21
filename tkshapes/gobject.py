import math
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
    GLineItem2,
    GRectItem,
    GOvalItem,
    GPolygonItem,
    GBufferGateBody,
)

class GObject:
    """
    A container for GItems. Can be added to a GCanvas.
    """

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

        # TODO: The GObject needs to keep track of the GItems it contains
        # TODO: IN-PROGRESS: Let's keep track of the GItems here.
        # TODO: Each GItem will have its own item-level name, so let's use a Dictionary
        # TODO: Key will be the GItem name, and value will be the actual object
        self._items = {}

        # TODO: We also need a mapping of canvas Item ID --> GItem, as there are cases
        # TODO: Where we have a canvas item ID, but need to know the GItem in order to
        # TODO: check some properties of it.  We might be able to get around this if
        # TODO: we move all lower-level canvas interaction within the GItems, but that
        # TODO: doesn't seem like an easy change...will think on it.
        # TODO:
        # TODO: Okay, i implemented get_item_by_id, but it's a for loop, and I'm not using
        # TODO: the below dictionary.  Instead i'm looping through self._items, which seems
        # TODO: okay for now, but I'd rather an O(n) function, so need to build out this
        # TODO: dictionary when each GItem is created, and I will re-write get_item_by_id()
        self._canvas_item_id_to_gitem = {}

        # Move to GItem?
        # this data is used to keep track of a canvas object being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # NOTE: selection will be done at the GObject level, but we also keep track of each GItem's
        # NOTE: selection status.
        #
        #    * GObject-level selection:
        #        - denotes the selection of the GObject as a whole
        #        - affected by Command-Click on the object, but only for GItems that are "draggable"
        #
        #    * GItem-level selection:
        #        - affects how the GItem is displayed (fill_color vs selected_fill_color)
        #
        # my selection status (am I selected or not)
        self._selected = False

        # Move to GItem?
        # all fillable canvas items will use these colors
        self.fill_color = 'white'
        self._selected_fill_color = '#1111FF'

        # Move to GItem?
        # current line width and active line width (changes when zooming in/out to maintain proper ratio)
        self.outline_width = 2.0
        self.outline_color = 'blue'
        self.active_outline_width = 5.0
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
        """ scale by scale factor x_scale and y_scale relative to point (x_offset, y_offset) """

        # scale the canvas items associated with self._tag
        self.gcanvas.canvas.scale(self._tag, x_offset, y_offset, x_scale, y_scale)

        # in theory, we could scale at different rates horizontally vs vertically, but
        # line widths are constant across the whole item, so we just pick the x_scale
        sf = x_scale

        # TODO: Figure out a way to speed this up.  As we get lots of GItems, zooming
        # TODO: slows down, and is choppy because of this for loop.  The background
        # TODO: GraphPaper adds a ton of GItems, so consider how we might get around
        # TODO: that.  Maybe we should write a special GCanvasBackground object, and
        # TODO: then we could optimize zooming by keeping all of those GItems out of
        # TODO: the dictionary of GItems. For now, let's skip scaling the BACKGROUND
        # TODO: items.

        if self._tag != "BACKGROUND":  #  <-- Temp hack to speed up zooming
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
        # TODO: Currently, it is assumed that if something is draggable, it is also selectable.  Not sure we want this.
        # TODO: We should be able to specify the GItems that are draggable (those we can click on and drag the entire
        # TODO: GObject), while also keeping to the idea that the selection happens at the GObject-level
        # TODO: the "draggable" property should only be used to specify that a GItem can be clicked-dragged
        # TODO: Generally (at least in the case of logic gates), we'd always click-drag the body of the gate, while
        # TODO: the input and output components would not be draggable.  Sames goes for "selectable", so the current
        # TODO: assumption works for now, so I'll leave it until a case comes up where this doens't work.

        # add bindings for selection toggle on/off using Command-Click
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<Command-ButtonPress-1>", self.on_command_button_press)

        # add bindings for click and hold to drag an object
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonPress-1>", self.on_button_press)
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonRelease-1>", self.on_button_release)
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<B1-Motion>", self.on_button_motion)

        # add bindings for right-click (could eventually be used for context-sensative menus)
        # TODO: not used yet, but we may want to use different callbacks to keep the code separate from
        # TODO: the click-drag-release code.  Otherwise use event.num to detect what button is being pressed.
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonPress-2>", self.on_button_press)
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonRelease-2>", self.on_button_release)

        # add bindings for <Enter> and <Leave> events
        self.gcanvas.canvas.tag_bind(self._tag, "<Enter>", self.on_enter)
        self.gcanvas.canvas.tag_bind(self._tag, "<Leave>", self.on_leave)

        # add binding to handle Selection virtual events from a selection box
        self.gcanvas.canvas.bind("<<Selection>>", self.on_selection_event, "+")

    def on_button_press(self, event):
        """ Beginning drag of an object - record the item and its location """
        print(f"DEBUG: CLICK   Button-{event.num} Item: {event.widget.find_withtag('current')}")
        self._drag_data["item"] = self.gcanvas.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_button_release(self, event):
        """ End drag of an object - reset the drag information """
        print(f"DEBUG: RELEASE Button-{event.num} Item: {event.widget.find_withtag('current')}")
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_button_motion(self, event):
        """ Handle dragging of an object """

        # This handler could be triggered by an accidental B1-Motion event while Command-Clicking to [de]select
        if self._drag_data["item"] is None:
            return

        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]

        # Let's start by getting the list of canvas items I'm composed of
        items_im_composed_of = self.gcanvas.canvas.find_withtag(self._tag)
        # Another way to get the list of items I'm composed of:
        #items_im_composed_of = [i.item for i in self._items.values()]
        #print("DEBUG: self._tag={} items_im_composed_of={}".format(self._tag, items_im_composed_of))

        #
        # We want to move all sub-objects/items, not just the one we clicked on.  So we
        # move all canvas items tagged with self._tag, which would be the whole GObject
        #
        # We also want to move any items tagged as "selected" which may have been selected
        # by the selection box.  However, if self._tag is contained within the selected set,
        # we dont want to move it twice, otherwise we end up with it moving twice as far on
        # the canvas.
        #
        # We have 2 cases to consider:
        #   1) Are we moving an item that is NOT selected?  If so, just move it.
        #   2) Or Are we moving an item that IS selected? If so, then move all "selected" items,
        #      which will already include the one we click-dragged
        #

        # get all tags on the 1st item in the list/tuple
        tags_on_1st_item = self.gcanvas.canvas.gettags(items_im_composed_of[0])

        # If one of the items in the GObject has the "selected" tag, they all will.
        # So, we can just check the 1st item to determine selection status.
        if "selected" in tags_on_1st_item:
            self.raise_with_tag("selected")
            self.gcanvas.canvas.move("selected", delta_x, delta_y)  # Case #1
        else:
            self.gcanvas.canvas.move(self._tag, delta_x, delta_y)   # Case #2

        # TODO: Something to think about -
        # TODO:
        # TODO: Looking at the above block, do we want to manipulate items directly (possibly for better performance)
        # TODO: Or do we want to make methods on the GItem objects to call to accomplish the same thing?
        # TODO:
        # TODO: All of the bindings are at the GObject-level, so I'm not sure we'll be able to fully get away from
        # TODO: direct manipulation of canvas items, but we should consider if we want to remember the current position
        # TODO: of a GItem, we'd have to use the interface to that object, rather than bypassing it and going directly
        # TODO: to the canvas items themselves.  Just something to keep in mind as we polish the code and object
        # TODO: interfaces.
        # TODO:
        # TODO: Ideally, we shouldn't rely on the item tags as a form of communication between the GObject and GItem,
        # TODO: but instead, the GItem should have a fully capable interface to allow us to do everything we need to do.
        # TODO:

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set(f"Dragging {self._tag} ...")

    def on_command_button_press(self, event):
        """ handle Command-Click on a GObject to toggle Selection """

        # convert from screen coords to canvas coords
        #canvas = event.widget
        #x = canvas.canvasx(event.x)
        #y = canvas.canvasy(event.y)
        #clicked_item = self.gcanvas.canvas.find_closest(x, y)[0]
        clicked_item = self.gcanvas.canvas.find_withtag('current')

        if self.selectable:
            self.toggle_selected()
            print("Item ID {} --> Command-Clicked --> Selected? {}".format(clicked_item, self._selected))
        else:
            print("Item {} not selectable.".format(clicked_item))

    def raise_with_tag(self, tag):
        items = self.gcanvas.canvas.find_withtag(tag)
        #print(f"Items found with tag: {tag} = {items}")
        for item in items:
            tags_on_item = self.gcanvas.canvas.gettags(item)
            #print(f"    --> Tags on item {item} = {tags_on_item}")
            if "raisable" in tags_on_item:
                self.gcanvas.canvas.tag_raise(item)

    def set_selected(self):
        if self.selectable:
            self._selected = True
            for item in self._items.values():
                #print(f"DEBUG: set_selected(): item = {item}")
                item.selected = True

    def clear_selected(self):
        if self.selectable:
            self._selected = False
            for item in self._items.values():
                #print(f"DEBUG: clear_selected(): item = {item}")
                item.selected = False

    def toggle_selected(self):
        if self.selectable:
            self._selected = not self._selected
            if (self._selected):
                self.set_selected()
            else:
                self.clear_selected()

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

    def get_item_by_id(self, id):
        """
        find the key in self._items that has value.item == id
        This allows us to map canvas item ID to the actual GItem object
        In other words, "Get GItem object ref by canvas item ID"
        """
        for i in self._items:
            current_id = self._items[i].item
            #print(f"DEBUG: get_item_by_id({id}) --> Checking {current_id}")
            if current_id in id or current_id == id:
                #print(f"DEBUG: get_item_by_id({id}) --> Found")
                return self._items[i]
        # if we get here, it wasn't found
        #print(f"DEBUG: get_item_by_id({id}) --> Not found")
        return None

    def on_enter(self, event):
        """ handle <Enter> events for GItem, including highlighting and raising """

        # TODO:
        # TODO:  There is a lot of shared logic at the head of on_enter() and on_leave(), so let's look at
        # TODO:  implementing some helper functions to DRY this out a bit.  One thing that would be helpful
        # TODO:  would be to take the entered_item_id, and then extract all the needed tagging info into a
        # TODO:  dictionary, so we can easily check things like highlight_groups, etc.
        # TODO:
        # TODO:  Also keep in mind, we want to be able to extract info from the tags quickly.  Currently we
        # TODO:  are tagging highlight_groups as a colon-separated thing like this:
        # TODO:
        # TODO:     highlight_group:group_name
        # TODO:
        # TODO:  ...where the "group_name" is just an arbitrary string we use to identify multiple groups
        # TODO:  within the same GObject.  If it becomes too much of a performance hit extracting that data,
        # TODO:  we could instead support only a single highlight group, and just look for that tag on each
        # TODO:  item, and if it exists, all of those items are in the group.  This would mean we could only
        # TODO:  have a single group of items that could be highlighted together per GObject, but this is
        # TODO:  probably fine.  So far I've not encountered the need/desire to have multiple multi-item
        # TODO:  groups.
        # TODO:

        # convert from screen coords to canvas coords
        #canvas = event.widget
        #x = canvas.canvasx(event.x)
        #y = canvas.canvasy(event.y)
        #entered_item_id = self.gcanvas.canvas.find_closest(x, y)[0]
        entered_item_id = self.gcanvas.canvas.find_withtag('current')

        tags_on_id = self.gcanvas.canvas.gettags(entered_item_id)

        if self._tag != 'BACKGROUND':
            print(f"DEBUG: on_enter(): item {entered_item_id} with tags {tags_on_id}: ")

            # I want to be able to get the GItem from entered_item_id, but need a mapping
            entered_item = self.get_item_by_id(entered_item_id)
            if entered_item:
                print(f"DEBUG: on_enter(): Entered GItem: {entered_item} with id {entered_item.item}")

            highlight_group_items = []
            for i in self._items:
                id = self._items[i].item
                tags_on_this_id = self.gcanvas.canvas.gettags(id)
                print(f"DEBUG: on_enter():     --> {i}: {id}: {tags_on_this_id}")

            if "raisable" in tags_on_id:
                self.gcanvas.canvas.tag_raise(self._tag)

            # Highlight the item where the event was triggered by manually setting outline and width
            if "highlightable" in tags_on_id:
                # we need to use the active_outline_color and active_outline_width of the GItem, not the GObject
                # how do we get the corresponding GItem, knowing only the item ID?
                self.gcanvas.canvas.itemconfigure(
                    entered_item_id,
                    outline=entered_item.active_outline_color,
                    width=entered_item.active_outline_width)

            # we also want to check for tag "activate_together", and if found, we want to highlight all
            # items that are also tagged with "activate_together".  For example, in a NotGate, we want
            # to highlight the body of the gate, and also the little bubble up front indicating the Not.
            # 1) check for the highlight_group:<name> tag on the item entered
            # 2) if it exists, then check to see what other items have the same tag
            # 3) then update all of those items to be highlighted

    def on_leave(self, event):
        # convert from screen coords to canvas coords
        #canvas = event.widget
        #x = canvas.canvasx(event.x)
        #y = canvas.canvasy(event.y)
        # For some reason the entered_item_id isn't always correct
        # but when i check the tags, I see the 'current' tag is always where i expect
        #left_item_id = self.gcanvas.canvas.find_closest(x, y)[0]
        left_item_id = self.gcanvas.canvas.find_withtag('current')
        tags_on_id = self.gcanvas.canvas.gettags(left_item_id)

        if self._tag != 'BACKGROUND':
            left_item = self.get_item_by_id(left_item_id)
            print(f"DEBUG: on_leave(): item {left_item_id} with tags {tags_on_id}: ")
            for i in self._items:
                id = self._items[i].item
                tags_on_this_id = self.gcanvas.canvas.gettags(id)
                print(f"DEBUG: on_leave():     --> {i}: {id}: {tags_on_this_id}")

            # De-highlight the item where the event was triggered by manually setting outline and width
            if "highlightable" in tags_on_id:
                self.gcanvas.canvas.itemconfigure(
                    left_item_id,
                    outline=left_item.outline_color,
                    width=left_item.outline_width)

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
        """ Make the GObject undraggable (immovable) across the canvas """
        for i in self._items:
            print(f"DEBUG: Setting GItem {i} dragability to False")
            self._items[i].draggable = False

    def make_draggable(self):
        """ Make the GObject draggable across the canvas """
        for i in self._items:
            print(f"DEBUG: Setting GItem {i} dragability to True")
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
        self._items['line1'].raisable = True

        self._items['line2'] = GLineItem(self.gcanvas, self._x, self._y + 4, self.length, self._tag)
        self._items['line2'].add()
        self._items['line2'].hidden = False
        self._items['line2'].draggable = False
        self._items['line2'].raisable = True

        self._items['line3'] = GLineItem(self.gcanvas, self._x, self._y + 8, self.length, self._tag)
        self._items['line3'].add()
        self._items['line3'].hidden = False
        self._items['line3'].draggable = False
        self._items['line3'].raisable = True

        self._items['line4'] = GLineItem(self.gcanvas, self._x, self._y + 12, self.length, self._tag)
        self._items['line4'].add()
        self._items['line4'].hidden = False
        self._items['line4'].draggable = False
        self._items['line4'].raisable = True

        self._items['oval1'] = GOvalItem(self.gcanvas, self._x, self._y + 16, self.length, self.length, self._tag)
        self._items['oval1'].add()
        self._items['oval1'].fill_color = '#aaaaaa'
        self._items['oval1'].selected_fill_color = '#ff0000'
        self._items['oval1'].outline_color = 'blue'
        self._items['oval1'].active_outline_color = 'orange'
        self._items['oval1'].outline_width = 2.0
        self._items['oval1'].active_outline_width = 5.0
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
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].show_selection = False

        self._items['input_line'] = GLineItem(self.gcanvas, self._x, self._y + 28, -10, self._tag)
        self._items['input_line'].add()
        self._items['input_line'].hidden = False
        self._items['input_line'].draggable = False

        self._items['input_dot'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 23, 10, 10, self._tag)
        self._items['input_dot'].add()
        self._items['input_dot'].fill_color = 'white'
        self._items['input_dot'].outline_color = 'blue'
        self._items['input_dot'].active_outline_color = 'orange'
        self._items['input_dot'].outline_width = 2.0
        self._items['input_dot'].active_outline_width = 5.0
        self._items['input_dot'].hidden = False
        self._items['input_dot'].draggable = False
        self._items['input_dot'].show_selection = False

        self._items['body'] = GBufferGateBody(self.gcanvas, self._x, self._y, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True


class GNotGate(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

    def add(self):

        self._items['output_line'] = GLineItem(self.gcanvas, self._x + 66, self._y + 28, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 76, self._y + 23, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].show_selection = False

        self._items['input_line'] = GLineItem(self.gcanvas, self._x, self._y + 28, -10, self._tag)
        self._items['input_line'].add()
        self._items['input_line'].hidden = False
        self._items['input_line'].draggable = False

        self._items['input_dot'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 23, 10, 10, self._tag)
        self._items['input_dot'].add()
        self._items['input_dot'].fill_color = 'white'
        self._items['input_dot'].outline_color = 'blue'
        self._items['input_dot'].active_outline_color = 'orange'
        self._items['input_dot'].outline_width = 2.0
        self._items['input_dot'].active_outline_width = 5.0
        self._items['input_dot'].hidden = False
        self._items['input_dot'].draggable = False
        self._items['input_dot'].show_selection = False

        self._items['not_dot'] = GOvalItem(self.gcanvas, self._x + 58, self._y + 24, 8, 8, self._tag)
        self._items['not_dot'].add()
        self._items['not_dot'].fill_color = 'white'
        self._items['not_dot'].outline_color = 'blue'
        self._items['not_dot'].active_outline_color = 'orange'
        self._items['not_dot'].outline_width = 2.0
        self._items['not_dot'].active_outline_width = 5.0
        self._items['not_dot'].hidden = False
        self._items['not_dot'].draggable = False
        self._items['not_dot'].show_selection = True
        self._items['not_dot'].highlight_group('body_plus_not_bubble')

        self._items['body'] = GBufferGateBody(self.gcanvas, self._x, self._y, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True
        self._items['body'].highlight_group('body_plus_not_bubble')


class GOrGate(GObject):
    """ Draw OR Gate on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []

    def add(self):

        x = self._x
        y = self._y

        # An OR gate has two input connections and one output connection
        # self.input_connection['IN_0'] = InputConnection(self, (x + 7, y + 17), 'Input 0')
        # self.input_connection['IN_1'] = InputConnection(self, (x + 7, y + 43), 'Input 1')
        # self.output_connection['OUT_0'] = OutputConnection(self, (x + 65, y + 30), 'Output')

        self._points.extend((x, y))  # first point in polygon

        # scale the unit circle by 30, as that's the distance from the center of the circle to the arc
        # See Also: https://en.wikipedia.org/wiki/Unit_circle
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 65) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        self._items['output_line'] = GLineItem(self.gcanvas, self._x + 65, self._y + 30, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 75, self._y + 25, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].show_selection = False

        self._items['input_line1'] = GLineItem(self.gcanvas, self._x + 7, self._y + 17, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 13, self._y + 12, 10, 10, self._tag)
        self._items['input_dot1'].add()
        self._items['input_dot1'].fill_color = 'white'
        self._items['input_dot1'].outline_color = 'blue'
        self._items['input_dot1'].active_outline_color = 'orange'
        self._items['input_dot1'].outline_width = 2.0
        self._items['input_dot1'].active_outline_width = 5.0
        self._items['input_dot1'].hidden = False
        self._items['input_dot1'].draggable = False
        self._items['input_dot1'].show_selection = False

        self._items['input_line2'] = GLineItem(self.gcanvas, self._x + 7, self._y + 43, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 13, self._y + 38, 10, 10, self._tag)
        self._items['input_dot2'].add()
        self._items['input_dot2'].fill_color = 'white'
        self._items['input_dot2'].outline_color = 'blue'
        self._items['input_dot2'].active_outline_color = 'orange'
        self._items['input_dot2'].outline_width = 2.0
        self._items['input_dot2'].active_outline_width = 5.0
        self._items['input_dot2'].hidden = False
        self._items['input_dot2'].draggable = False
        self._items['input_dot2'].show_selection = False

        self._items['body'] = GPolygonItem(self.gcanvas, self._points, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True


class GXOrGate(GObject):
    """ Draw XOR Gate on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._arc1_points = []
        self._arc2_points = []

    def add(self):

        x = self._x
        y = self._y

        self._arc1_points.extend((x, y))  # first point in polygon

        # scale the unit circle by 30, as that's the distance from the center of the circle to the arc
        # See Also: https://en.wikipedia.org/wiki/Unit_circle
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 65) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc1_points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + x
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc1_points.extend((arc_x, arc_y))

        # Arc2 is the extra line on the back of the XOR gate
        self._arc2_points.extend((x - 8, y))  # first point in polygon

        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 8) + (x - 8)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc2_points.extend((arc_x, arc_y))

        for angle in range(90, 270):
            arc_x = (math.cos(math.radians(angle)) * -8) + (x - 8)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._arc2_points.extend((arc_x, arc_y))

        self._items['output_line'] = GLineItem(self.gcanvas, self._x + 65, self._y + 30, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 75, self._y + 25, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].show_selection = False

        self._items['input_line1'] = GLineItem(self.gcanvas, self._x, self._y + 17, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 12, 10, 10, self._tag)
        self._items['input_dot1'].add()
        self._items['input_dot1'].fill_color = 'white'
        self._items['input_dot1'].outline_color = 'blue'
        self._items['input_dot1'].active_outline_color = 'orange'
        self._items['input_dot1'].outline_width = 2.0
        self._items['input_dot1'].active_outline_width = 5.0
        self._items['input_dot1'].hidden = False
        self._items['input_dot1'].draggable = False
        self._items['input_dot1'].show_selection = False

        self._items['input_line2'] = GLineItem(self.gcanvas, self._x, self._y + 43, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 38, 10, 10, self._tag)
        self._items['input_dot2'].add()
        self._items['input_dot2'].fill_color = 'white'
        self._items['input_dot2'].outline_color = 'blue'
        self._items['input_dot2'].active_outline_color = 'orange'
        self._items['input_dot2'].outline_width = 2.0
        self._items['input_dot2'].active_outline_width = 5.0
        self._items['input_dot2'].hidden = False
        self._items['input_dot2'].draggable = False
        self._items['input_dot2'].show_selection = False

        self._items['body'] = GPolygonItem(self.gcanvas, self._arc1_points, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True

        self._items['arc2'] = GPolygonItem(self.gcanvas, self._arc2_points, self._tag)
        self._items['arc2'].add()
        self._items['arc2'].fill_color = 'white'
        self._items['arc2'].outline_color = 'blue'
        self._items['arc2'].active_outline_color = 'orange'
        self._items['arc2'].outline_width = 2.0
        self._items['arc2'].active_outline_width = 5.0
        self._items['arc2'].hidden = False
        self._items['arc2'].draggable = True
        self._items['arc2'].show_selection = False


class GAndGate(GObject):
    """ Draw AND Gate on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []

    def add(self):

        x = self._x
        y = self._y

        self._points.extend((x, y))  # first point in polygon
        self._points.extend((x + 29, y))

        # scale the unit circle by 30, as that's the distance from the center of the circle to the arc
        # See Also: https://en.wikipedia.org/wiki/Unit_circle
        for angle in range(-90, 90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 29)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x, y + 60))  # last point in polygon, which connects back to the 1st point

        self._items['output_line'] = GLineItem(self.gcanvas, self._x + 59, self._y + 30, 10, self._tag)
        self._items['output_line'].add()
        self._items['output_line'].hidden = False
        self._items['output_line'].draggable = False

        self._items['output_dot'] = GOvalItem(self.gcanvas, self._x + 69, self._y + 25, 10, 10, self._tag)
        self._items['output_dot'].add()
        self._items['output_dot'].fill_color = 'white'
        self._items['output_dot'].outline_color = 'blue'
        self._items['output_dot'].active_outline_color = 'orange'
        self._items['output_dot'].outline_width = 2.0
        self._items['output_dot'].active_outline_width = 5.0
        self._items['output_dot'].hidden = False
        self._items['output_dot'].draggable = False
        self._items['output_dot'].show_selection = False

        self._items['input_line1'] = GLineItem(self.gcanvas, self._x, self._y + 17, -10, self._tag)
        self._items['input_line1'].add()
        self._items['input_line1'].hidden = False
        self._items['input_line1'].draggable = False

        self._items['input_dot1'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 12, 10, 10, self._tag)
        self._items['input_dot1'].add()
        self._items['input_dot1'].fill_color = 'white'
        self._items['input_dot1'].outline_color = 'blue'
        self._items['input_dot1'].active_outline_color = 'orange'
        self._items['input_dot1'].outline_width = 2.0
        self._items['input_dot1'].active_outline_width = 5.0
        self._items['input_dot1'].hidden = False
        self._items['input_dot1'].draggable = False
        self._items['input_dot1'].show_selection = False

        self._items['input_line2'] = GLineItem(self.gcanvas, self._x, self._y + 43, -10, self._tag)
        self._items['input_line2'].add()
        self._items['input_line2'].hidden = False
        self._items['input_line2'].draggable = False

        self._items['input_dot2'] = GOvalItem(self.gcanvas, self._x - 20, self._y + 38, 10, 10, self._tag)
        self._items['input_dot2'].add()
        self._items['input_dot2'].fill_color = 'white'
        self._items['input_dot2'].outline_color = 'blue'
        self._items['input_dot2'].active_outline_color = 'orange'
        self._items['input_dot2'].outline_width = 2.0
        self._items['input_dot2'].active_outline_width = 5.0
        self._items['input_dot2'].hidden = False
        self._items['input_dot2'].draggable = False
        self._items['input_dot2'].show_selection = False

        self._items['body'] = GPolygonItem(self.gcanvas, self._points, self._tag)
        self._items['body'].add()
        self._items['body'].fill_color = 'white'
        self._items['body'].outline_color = 'blue'
        self._items['body'].active_outline_color = 'orange'
        self._items['body'].outline_width = 2.0
        self._items['body'].active_outline_width = 5.0
        self._items['body'].hidden = False
        self._items['body'].draggable = True
        self._items['body'].show_selection = True


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

        self._items['GRect'] = GRectItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['GRect'].add()
        self._items['GRect'].fill_color = 'white'
        self._items['GRect'].outline_color = 'blue'
        self._items['GRect'].active_outline_color = 'orange'
        self._items['GRect'].outline_width = 2.0
        self._items['GRect'].active_outline_width = 5.0
        self._items['GRect'].hidden = False
        self._items['GRect'].draggable = True
        self._items['GRect'].show_selection = True


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

        self._items['GOval'] = GOvalItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['GOval'].add()
        self._items['GOval'].fill_color = 'white'
        self._items['GOval'].outline_color = 'blue'
        self._items['GOval'].active_outline_color = 'orange'
        self._items['GOval'].outline_width = 2.0
        self._items['GOval'].active_outline_width = 5.0
        self._items['GOval'].hidden = False
        self._items['GOval'].draggable = True
        self._items['GOval'].show_selection = True


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
            self._items['graph_paper_vline'+str(i)] = GLineItem2(self.gcanvas, points, self._tag)
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
            self._items['graph_paper_hline'+str(i)] = GLineItem2(self.gcanvas, points, self._tag)
            self._items['graph_paper_hline'+str(i)].add()
            self._items['graph_paper_hline'+str(i)].fill_color = line_color
            self._items['graph_paper_hline'+str(i)].outline_width = 1.0
            self._items['graph_paper_hline'+str(i)].active_outline_width = 1.0
            self._items['graph_paper_hline'+str(i)].hidden = False
            self._items['graph_paper_hline'+str(i)].raisable = False
            self._items['graph_paper_hline'+str(i)].draggable = False
            self._items['graph_paper_hline'+str(i)].selectable = False

