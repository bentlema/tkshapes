import math
import cmath
import itertools

from .gitem import (
    GLineItem,
    GWireItem,
    GHorzLineItem,
    GVertLineItem,
    GRectItem,
    GOvalItem,
    GPolygonItem,
)


def grouper(iterable, n, fillvalue=None):
    """
    Collect data into fixed-length chunks or blocks
    Example:  grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


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

        # Remember my GItems - Key is the GItem name, and Value is the actual GItem object
        self._items = {}

        # For "Connectable" types, remember data about our connection nodes
        # Each Connectable GObject can have one or more nodes that can be connected to
        # other GObject nodes via a "Connector" type (e.g. GWire)
        self._nodes = {}

        # For "Connector" types, we can have a GConnection object
        self.connection = None

        # Keep track of a canvas object being dragged
        self._drag_data = {
            "x": 0,
            "y": 0,
            "item": None
        }

        # Keep track of a connection as we are selecting the starting and ending points
        self._connection_data = {
            "start_x": 0,
            "start_y": 0,
            "line1": None,
            "line2": None,
        }

        # NOTE: selection is done at the GObject level, but we also keep track of each GItem's
        # NOTE: selection status.
        #
        #    * GObject-level selection:
        #        - denotes the selection of the GObject as a whole
        #        - affected by Command-Click on the object, but only for GItems that are "draggable"
        #
        #    * GItem-level selection:
        #        - affects how the GItem is displayed (fill_color vs selected_fill_color)

        # my selection status (am I selected or not)
        self._selected = False

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
        self._connectable = False     # if the GObject can be connected to another connectable GObject
        self._connector = False       # if the GObject is a connector, such as a GWire

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

        # add bindings for making connections
        self.gcanvas.canvas.tag_bind(self._tag + ":connectable_initiator", "<ButtonPress-1>", self.on_start_connection)
        self.gcanvas.canvas.tag_bind(self._tag + ":connectable_initiator", "<ButtonRelease-1>", self.on_end_connection)
        self.gcanvas.canvas.tag_bind(self._tag + ":connectable_initiator", "<B1-Motion>", self.on_making_connection)

        # add bindings for right-click (could eventually be used for context-sensitive menus)
        # TODO: not used yet, but we may want to use different callbacks to keep the code separate from
        # TODO: the click-drag-release code.  Otherwise use event.num to detect what button is being pressed.
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonPress-2>", self.on_button_press)
        self.gcanvas.canvas.tag_bind(self._tag + ":draggable", "<ButtonRelease-2>", self.on_button_release)

        # add bindings for <Enter> and <Leave> events
        self.gcanvas.canvas.tag_bind(self._tag, "<Enter>", self.on_enter)
        self.gcanvas.canvas.tag_bind(self._tag, "<Leave>", self.on_leave)

        # add binding to handle Selection virtual events from a selection box
        self.gcanvas.canvas.bind("<<Selection>>", self.on_selection_event, "+")

    def on_start_connection(self, event):
        """ Initiate connection """
        canvas_item = event.widget.find_withtag('current')
        print(f"DEBUG: BEGIN CONNECTION - Button-{event.num} Item: {canvas_item}")
        self._drag_data["item"] = canvas_item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Find GItem from Canvas Item ID
        g_item = self.get_item_by_id(canvas_item)
        x, y = g_item.center_point()

        # convert from screen coords to canvas coords
        #x = self.gcanvas.canvas.canvasx(event.x)
        #y = self.gcanvas.canvas.canvasy(event.y)
        self._connection_data["start_x"] = x
        self._connection_data["start_y"] = y

    def on_end_connection(self, event):
        """ Terminate connection """

        if self._connection_data["line1"] is not None:
            self.gcanvas.canvas.delete(self._connection_data["line1"])

        if self._connection_data["line2"] is not None:
            self.gcanvas.canvas.delete(self._connection_data["line2"])

        # Get start data
        connect_from_item = self._drag_data["item"]
        from_g_object = self.gcanvas.get_gobject_by_id(connect_from_item)
        from_g_item = from_g_object.get_item_by_id(connect_from_item)
        from_node_name = from_g_object.get_node_name_by_g_item(from_g_item)
        print(f"DEBUG: START CONNECTION")
        print(f"       --> GObject: {from_g_object}")
        print(f"       -->   GItem: {from_g_item} {connect_from_item}")
        print(f"       -->   GNode: {from_node_name}")
        print(f"       -->   Start: {int(self._connection_data['start_x'])} x {int(self._connection_data['start_y'])}")

        # convert from screen coords to canvas coords
        x = self.gcanvas.canvas.canvasx(event.x)
        y = self.gcanvas.canvas.canvasy(event.y)

        # TODO: we need to check for the closest, but also check for closest that is a GNode, otherwise if there is
        # TODO: another GWire close by, it could find that one instead.
        connect_to_item = self.gcanvas.canvas.find_closest(x, y)

        if connect_to_item:
            g_object = self.gcanvas.get_gobject_by_id(connect_to_item)

        if g_object:
            g_item = g_object.get_item_by_id(connect_to_item)

        if g_item and g_item.connectable_terminator:
            to_node_name = g_object.get_node_name_by_g_item(g_item)
        else:
            print(f"DEBUG: GItem is NOT a connection_terminator")
            # reject the GItem
            g_item = to_node_name = None

        if to_node_name:
            print(f"DEBUG: END CONNECTION - Button-{event.num}")
            print(f"       --> GObject: {g_object}")
            print(f"       -->   GItem: {g_item} {connect_to_item}")
            print(f"       -->   GNode: {to_node_name}")
            print(f"       -->     End: {int(x)} x {int(y)}")

            coords = (
                int(self._connection_data['start_x']),
                int(self._connection_data['start_y']),
                int(x),
                int(y),
            )

            # TODO: add a method to get GObject name, rather than use protected member "_tag" directly
            new_wire_name = from_g_object._tag + "_" + from_node_name + "__to__" + g_object._tag + "_" + to_node_name
            print(f"DEBUG: FINALIZE CONNECTION")
            print(f"       -->     Coords: {coords}")
            print(f"       -->       Name: {new_wire_name}")
            new_wire = self.gcanvas.create('GWire', coords, name=new_wire_name)

            new_wire.connect(
                from_g_object.node(from_node_name),
                g_object.node(to_node_name)
            )
            new_wire.update()
        else:
            print(f"DEBUG: END CONNECTION - Button-{event.num}")
            print(f"       --> Where?")

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set(f"Terminate Connection {self._tag} at {x}x{y}")

        # reset drag data for next event
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_making_connection(self, event):
        """ Moving from start point to end point of the connection """

        # This handler could be triggered by an accidental B1-Motion event while Command-Clicking to [de]select
        if self._drag_data["item"] is None:
            return

        # convert from screen coords to canvas coords
        x = self.gcanvas.canvas.canvasx(event.x)
        y = self.gcanvas.canvas.canvasy(event.y)

        #
        # TODO: This is where we should draw the connection wire/line using whatever connection_style is set
        #
        # TODO: Need to grab the center point of the connectable oval so that we can start drawing our line
        # TODO: from the exact center point to make it pretty.  For now, we'll just start drawing it from the
        # TODO: point our mouse pointer clicked at, which could be off-center quite a bit.
        self.draw_connection((x, y))

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set(f"Making Connection {self._tag} at {x} x {y}")

    def draw_connection(self, point):
        x, y = point
        zl = self.gcanvas.zoom_level
        line_width1 = zl * 5.0
        line_width2 = zl * 2.0

        if self._connection_data["line1"] is not None:
            self.gcanvas.canvas.delete(self._connection_data["line1"])

        if self._connection_data["line2"] is not None:
            self.gcanvas.canvas.delete(self._connection_data["line2"])

        # These are the points we will use to draw our lines
        points = (int(self._connection_data["start_x"]), int(self._connection_data["start_y"]), int(x), int(y))
        points = self.smooth_coords(points)

        self._connection_data["line1"] = self.gcanvas.canvas.create_line(
            points, width=line_width1, fill='blue', capstyle="round", smooth=True, splinesteps=20)

        self._connection_data["line2"] = self.gcanvas.canvas.create_line(
            points, width=line_width2, fill='white', capstyle="round", smooth=True, splinesteps=20)

        self.gcanvas.canvas.tag_raise(self._connection_data["line1"])
        self.gcanvas.canvas.tag_raise(self._connection_data["line2"])


    def on_button_press(self, event):
        """ Beginning drag of an object - record the item and its location """
        #print(f"DEBUG: CLICK   Button-{event.num} Item: {event.widget.find_withtag('current')}")
        #self._drag_data["item"] = self.gcanvas.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["item"] = event.widget.find_withtag('current')
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_button_release(self, event):
        """ End drag of an object - reset the drag information """
        #print(f"DEBUG: RELEASE Button-{event.num} Item: {event.widget.find_withtag('current')}")
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

            # TODO:  THIS WHOLE SECTION NEEDS TO BE DRY'ed OUT
            # TODO:  vvv
            # deal with updating connections - get any and all GObjects on the canvas that are selected,
            # and make sure we update any connections to any of them as we drag one.
            # first get list of all GObjects involved
            items_selected = self.gcanvas.canvas.find_withtag("selected")
            # of the selected items, which ones have active connections?
            # first we need to get the GObject that corresponds to the canvas item
            for c_item in items_selected:
                g_object = self.gcanvas.get_gobject_by_id((c_item,))
                if g_object._nodes:
                    #print(f"DEBUG: GObject {g_object} has nodes {g_object._nodes}")
                    for g_node_name in g_object._nodes:
                        g_node = g_object._nodes[g_node_name]
                        # check if our g_node has connections
                        if g_node.connections:
                            for conn in g_node.connections:
                                # if we have any connections, update the location of the connection g_object
                                conn.g_object.update()
            # TODO:  ^^^
            # TODO:  THIS WHOLE SECTION NEEDS TO BE DRY'ed OUT
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
        # TODO: At the same time, we could look at the above as an optimization.  Not doing that would mean doing
        # TODO: a "for each GItem do..." loop, and then implementing a move() method on each GItem, which seems...?
        # TODO:

        # If we are moving a GObject that is connectable, we need to ensure we send a message to any
        # connected GObjects to update themselves (re-draw)
        #
        # This means that we need to know what GObject(s) we are connected to
        # As we are dragging an entire GObject, we shouldn't need to know the exact GItems that need to be updated
        # rather, we just send a message to any connected GObjects to redraw themselves.

        # if we have a connection, make sure to update them too
        # first check if we have any GNodes, and if those GNodes have connections
        if self._nodes:
            for g_node_name in self._nodes:
                g_node = self._nodes[g_node_name]
                # check if our g_node has connections
                if g_node.connections:
                    for conn in g_node.connections:
                        # if we have any connections, update the location of the connection g_object
                        conn.g_object.update()

        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # convert from screen coords to canvas coords
        x = event.widget.canvasx(event.x)
        y = event.widget.canvasy(event.y)

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set(f"Dragging {self._tag} at {x}x{y}")

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
            if self._selected:
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

        # TODO: make this more forgiving, so that id can come in as
        # TODO: an int or a tuple
        for i in self._items:
            current_id = self._items[i].item
            #print(f"DEBUG: get_item_by_id({id}) --> Checking {current_id}")
            if current_id in id or current_id == id:
                #print(f"DEBUG: get_item_by_id({id}) --> Found")
                return self._items[i]
        # if we get here, it wasn't found
        #print(f"DEBUG: get_item_by_id({id}) --> Not found")
        return None

    def get_node_name_by_g_item(self, g_item):
        for node_name in self._nodes:
            if self._nodes[node_name].g_item is g_item:
                return node_name
        return None

    def on_enter(self, event):
        self.on_enter_leave("enter")

    def on_leave(self, event):
        self.on_enter_leave("leave")

    def on_enter_leave(self, direction):
        if self._tag != 'BACKGROUND':
            canvas_item_id = self.gcanvas.canvas.find_withtag('current')

            # get the GItem from item_id
            g_item = self.get_item_by_id(canvas_item_id)

            #if g_item:
            #    if direction is "enter":
            #        print(f"DEBUG: Entered GItem: {g_item} with id {g_item.item}")
            #    else:
            #        print(f"DEBUG: Leaving GItem: {g_item} with id {g_item.item}")

            if direction is "enter" and g_item.raisable:
                # we should be calling GItem.raise_up() but this is faster
                self.gcanvas.canvas.tag_raise(self._tag)

                # TODO:  need to come up with some way to always raise up the
                # TODO:  GWire after raiseing up a GObject upon <Enter>
                # The following isn't ideal.  The weird case that can happen is
                # when things overlap, and one GObject is raised over another, but
                # its wire is "left behind" showing above another.  We could walk
                # through the connection/node objects and find the neighbors, and
                # then raise only those.
                # TODO: write a find_neighbors() method, which would find the next
                # TODO: hop through nodes/connections, then we should be able to
                # TODO: call tag_raise like this:
                #
                # for neighbor in self.find_neighbors():
                #     self.gcanvas.canvas.tag_raise(neighbor._tag)
                #
                # For now, we'll just do this:
                self.gcanvas.canvas.tag_raise("always_on_top")

            # (de)highlight the item where the event was triggered by manually setting outline and width
            if g_item.highlightable:
                if direction is "enter":  # <Enter>
                    highlighted = True
                else:                     # <Leave>
                    highlighted = False

                if not g_item.highlight_group:
                    g_item.highlighted = highlighted
                else:
                    for sibling_g_item in self._items.values():
                        if sibling_g_item.highlightable and sibling_g_item.highlight_group == g_item.highlight_group:
                            sibling_g_item.highlighted = highlighted

    def hide(self):
        for item in self._items.values():
            item.hidden = True

    def show(self):
        for item in self._items.values():
            item.hidden = False

    def redraw(self):
        """ do whatever is necessary to re-draw the GObject """
        print(f"DEBUG: Draw GObject {self}")

    def node(self, name):
        return self._nodes[name]

    def connect(self, node1, node2):
        """ connect one GObject's GNode to another """
        print(f"DEBUG: connect():")
        print(f"DEBUG:      GConnection:  {self.connection} g_object: {self.connection.g_object}")
        print(f"DEBUG:      GNode1: {node1} id: {node1.id} name: '{node1.name}'")
        print(f"DEBUG:      GNode2: {node2} id: {node2.id} name: '{node2.name}'")
        # At this point, our GConnection, GNode1, and GNode2 objects are
        # not fully populated.  We need to configure some things:
        self.connection.g_nodes = [node1, node2]
        node1.connections.append(self.connection)
        node2.connections.append(self.connection)
        # At this point our GConnection, and GNode objects are fully populated, though
        # we need to eventually add some checks here to make sure we've not hit any of
        # the max settings, and if the things we're trying to connect are valid

    def smooth_coords(self, coords):
        """ takes a 4-tuple of coordinates and returns the augmented coords """

        zl = self.gcanvas.zoom_level
        x1 = coords[0]
        y1 = coords[1]
        x2 = coords[2]
        y2 = coords[3]

        # Insert a couple mid-points so our line is nice and smooth
        new_coords = (
            x1, y1,
            x1 + (zl * 20), y1,
            x2 - (zl * 20), y2,
            x2, y2,
        )
        return new_coords

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

    @property
    def connector(self):
        return self._connector

    @connector.setter
    def connector(self, value):
        self._connector = bool(value)


class GWire(GObject):
    """ Draw Wire connecting two connectable GObjects """

    def __init__(self, *args, **kwargs):
        initial_coords = args[0]  # should be a 4-tuple
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(0, 0, name_tag)

        # We are a connector object (used for connecting two connectable GObjects)
        self.connector = True

        # Connector GObjects keep track of what they are connected to
        self.connection = GConnection(name=name_tag, g_object=self)

        # As the GWire will need to move with other objects are they are re-positioned
        # we will need to remember and track the two end points, and also implement
        # methods to move and redraw.
        self._coords = initial_coords

    def add(self):

        coords = self.smooth_coords(self._coords)

        # We draw a fat line first, and then draw a thicker white line on top to
        # make it look like a wire.
        self._items['fat_line'] = GWireItem(self.gcanvas, coords, self._tag)
        self._items['fat_line'].add()
        self._items['fat_line'].outline_color = 'blue'
        self._items['fat_line'].outline_width = 5.0 * self.gcanvas.zoom_level
        self._items['fat_line'].hidden = False
        self._items['fat_line'].draggable = False
        self._items['fat_line'].always_on_top = True

        self._items['thin_line'] = GWireItem(self.gcanvas, coords, self._tag)
        self._items['thin_line'].add()
        self._items['thin_line'].outline_color = 'white'
        self._items['thin_line'].outline_width = 2.0 * self.gcanvas.zoom_level
        self._items['thin_line'].hidden = False
        self._items['thin_line'].draggable = False
        self._items['thin_line'].always_on_top = True

    def coords(self, coords):
        self._coords = coords

    def redraw(self):
        for g_item_name in self._items:
            g_item = self._items[g_item_name]
            g_item.coords = self.smooth_coords(self._coords)
            g_item.raise_up()
            g_item.redraw()

    def move_to(self, coords):
        self.coords(coords)
        self.redraw()

    def update(self):
        """ check if we have any GNode connections, update our coords, and redraw """
        coords = []
        if self.connection.g_nodes:
            #print(f"** DEBUG: {self}")
            #print(f"** DEBUG: {self.connection}")
            #print(f"** DEBUG: {self.connection.g_nodes}")
            for g_node in self.connection.g_nodes:
                #print(f"** DEBUG:      g_node.name: {g_node.name}")
                #print(f"** DEBUG:      g_node.g_item: {g_node.g_item} {g_node.g_item.item}")
                (x, y) = g_node.g_item.center_point()
                coords.extend([x, y])
            #print(f"DEBUG: update(): Calculated new coords for GWire {coords}")
            self.move_to(coords)


class GBufferGate(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []

    def add(self):

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 58, self._y + 28, 10, self._tag)
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
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GBufferGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line'] = GHorzLineItem(self.gcanvas, self._x, self._y + 28, -10, self._tag)
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
        self._items['input_dot'].connectable_terminator = True

        self._nodes['input'] = GNode(name="GBufferGate Input", g_object=self, g_item=self._items['input_dot'])

        self._points.extend((self._x, self._y))  # first point in polygon
        self._points.extend((self._x + 58, self._y + 28))
        self._points.extend((self._x + 0, self._y + 56))

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


class GNotGate(GObject):

    def __init__(self, *args, **kwargs):

        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []

    def add(self):
        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 66, self._y + 28, 10, self._tag)
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
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GNotGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line'] = GHorzLineItem(self.gcanvas, self._x, self._y + 28, -10, self._tag)
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
        self._items['input_dot'].connectable_terminator = True

        self._nodes['input'] = GNode(name="GNotGate Input", g_object=self, g_item=self._items['input_dot'])

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
        self._items['not_dot'].highlight_group = 'body_plus_not_bubble'

        self._points.extend((self._x, self._y))  # first point in polygon
        self._points.extend((self._x + 58, self._y + 28))
        self._points.extend((self._x + 0, self._y + 56))

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
        self._items['body'].highlight_group = 'body_plus_not_bubble'


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

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 65, self._y + 30, 10, self._tag)
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
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GOrGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line1'] = GHorzLineItem(self.gcanvas, self._x + 7, self._y + 17, -10, self._tag)
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
        self._items['input_dot1'].connectable_terminator = True

        self._nodes['input_1'] = GNode(name="GOrGate Input 1", g_object=self, g_item=self._items['input_dot1'])

        self._items['input_line2'] = GHorzLineItem(self.gcanvas, self._x + 7, self._y + 43, -10, self._tag)
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
        self._items['input_dot2'].connectable_terminator = True

        self._nodes['input_2'] = GNode(name="GOrGate Input 2", g_object=self, g_item=self._items['input_dot2'])

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

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 65, self._y + 30, 10, self._tag)
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
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GXOrGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line1'] = GHorzLineItem(self.gcanvas, self._x, self._y + 17, -10, self._tag)
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
        self._items['input_dot1'].connectable_terminator = True

        self._nodes['input_1'] = GNode(name="GXOrGate Input 1", g_object=self, g_item=self._items['input_dot1'])

        self._items['input_line2'] = GHorzLineItem(self.gcanvas, self._x, self._y + 43, -10, self._tag)
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
        self._items['input_dot2'].connectable_terminator = True

        self._nodes['input_2'] = GNode(name="GXOrGate Input 2", g_object=self, g_item=self._items['input_dot2'])

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
        self._items['body'].highlight_group = 'body_plus_arc2'

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
        self._items['arc2'].highlight_group = 'body_plus_arc2'


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

        self._items['output_line'] = GHorzLineItem(self.gcanvas, self._x + 59, self._y + 30, 10, self._tag)
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
        self._items['output_dot'].connectable_initiator = True
        self._items['output_dot'].show_selection = False

        self._nodes['output'] = GNode(name="GAndGate Output", g_object=self, g_item=self._items['output_dot'])

        self._items['input_line1'] = GHorzLineItem(self.gcanvas, self._x, self._y + 17, -10, self._tag)
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
        self._items['input_dot1'].connectable_terminator = True

        self._nodes['input_1'] = GNode(name="GAndGate Input 1", g_object=self, g_item=self._items['input_dot1'])

        self._items['input_line2'] = GHorzLineItem(self.gcanvas, self._x, self._y + 43, -10, self._tag)
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
        self._items['input_dot2'].connectable_terminator = True

        self._nodes['input_2'] = GNode(name="GAndGate Input 2", g_object=self, g_item=self._items['input_dot2'])

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

        # Adjust width and height for current zoom level
        self._width *= self.gcanvas.zoom_level
        self._height *= self.gcanvas.zoom_level

        self._items['GRect'] = GRectItem(self.gcanvas, self._x, self._y, self._width, self._height, self._tag)
        self._items['GRect'].add()
        self._items['GRect'].fill_color = 'white'
        self._items['GRect'].outline_color = 'blue'
        self._items['GRect'].active_outline_color = 'orange'
        self._items['GRect'].outline_width = 2.0 * self.gcanvas.zoom_level
        self._items['GRect'].active_outline_width = 5.0 * self.gcanvas.zoom_level
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


class GPythonLogo(GObject):
    """ Draw Python Logo on the GCanvas """

    def __init__(self, *args, **kwargs):
        initial_x = args[0]
        initial_y = args[1]
        name_tag = kwargs['name']

        # Initialize parent GObject class
        super().__init__(initial_x, initial_y, name_tag)

        self._points = []
        self._rotated_points = []
        self._zoomed_points = []
        self._zoomed_rotated_points = []

    def add(self):

        x = self._x
        y = self._y

        self._points.extend((x, y + 68))  # first point in polygon

        # starting at top left snake mouth
        for angle in range(-180, -90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 29)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(-90, 0):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 126)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 30)
            self._points.extend((arc_x, arc_y))

        for angle in range(0, 90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x + 126)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 122)
            self._points.extend((arc_x, arc_y))

        for angle in range(-90, 0):
            arc_x = (math.cos(math.radians(angle)) * -42) + (x + 30)
            arc_y = (math.sin(math.radians(angle)) * 42) + (y + 194)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x - 12, y + 238))

        for angle in range(90, 180):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x - 50)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 208)
            self._points.extend((arc_x, arc_y))

        for angle in range(-180, -90):
            arc_x = (math.cos(math.radians(angle)) * 30) + (x - 50)
            arc_y = (math.sin(math.radians(angle)) * 30) + (y + 110)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x + 78, y + 80))
        self._points.extend((x + 78, y + 68))
        self._points.extend((x + 32, y + 68))
        self._points.extend((x + 32, y + 50))

        for angle in range(-270, 90):
            arc_x = (math.cos(math.radians(angle)) * 15) + (x + 32)
            arc_y = (math.sin(math.radians(angle)) * 15) + (y + 32)
            self._points.extend((arc_x, arc_y))

        self._points.extend((x + 32, y + 68))

        # the mathematical formulas to scale a point (x,y) by a factor of S relative to the point (cx, cy) are:
        # x_new = (S * (x - cx)) + cx
        # y_new = (S * (y - cy)) + cy

        cx = x + 78
        cy = y + 158

        self._zoomed_points = []
        for xx, yy in grouper(self._points, 2):
            x_new = (self.gcanvas.zoom_level * (xx - cx)) + cx
            y_new = (self.gcanvas.zoom_level * (yy - cy)) + cy
            self._zoomed_points.extend((x_new, y_new))

        self._items['blue_snake'] = GPolygonItem(self.gcanvas, self._zoomed_points, self._tag)
        self._items['blue_snake'].add()
        self._items['blue_snake'].fill_color = '#4B8BBE'
        self._items['blue_snake'].outline_color = '#4B8BBE'
        self._items['blue_snake'].active_outline_color = '#4B8BBE'
        self._items['blue_snake'].outline_width = 1.0
        self._items['blue_snake'].active_outline_width = 1.0
        self._items['blue_snake'].hidden = False
        self._items['blue_snake'].draggable = True
        self._items['blue_snake'].show_selection = False
        self._items['blue_snake'].show_highlight = False

        # I want to make a second snake rotated 180 degrees
        # See: http://effbot.org/zone/tkinter-complex-canvas.htm
        angle = 3.14159  # 3.14159 radians = 180 degrees
        cangle = cmath.exp(angle * 1j)

        # we will rotate about x,y
        center = complex(cx, cy)
        self._rotated_points = []
        for xx, yy in grouper(self._points, 2):
            v = cangle * (complex(xx, yy) - center) + center
            self._rotated_points.extend((v.real, v.imag))

        self._zoomed_rotated_points = []
        for xx, yy in grouper(self._rotated_points, 2):
            x_new = (self.gcanvas.zoom_level * (xx - cx)) + cx
            y_new = (self.gcanvas.zoom_level * (yy - cy)) + cy
            self._zoomed_rotated_points.extend((x_new, y_new))

        self._items['orange_snake'] = GPolygonItem(self.gcanvas, self._zoomed_rotated_points, self._tag)
        self._items['orange_snake'].add()
        self._items['orange_snake'].fill_color = '#FFD43B'
        self._items['orange_snake'].outline_color = '#FFD43B'
        self._items['orange_snake'].active_outline_color = '#FFD43B'
        self._items['orange_snake'].outline_width = 1.0
        self._items['orange_snake'].active_outline_width = 1.0
        self._items['orange_snake'].hidden = False
        self._items['orange_snake'].draggable = True
        self._items['orange_snake'].show_selection = False
        self._items['orange_snake'].show_highlight = False


class GNode:

    # Class variable to keep track of next available ID
    last_id = 100000000

    def __init__(self, name, g_object, g_item):
        self.id = self.next_id()
        self.name = name
        self.g_object = g_object
        self.g_item = g_item
        self.connections = []
        self.max_connections = 1

    def next_id(self):
        GNode.last_id += 1
        return GNode.last_id


class GConnection:

    # Class variable to keep track of next available ID
    last_id = 1000000000

    def __init__(self, name, g_object):
        self.id = self.next_id()
        self.name = name
        self.g_object = g_object
        self.g_nodes = []
        self.max_nodes = 2
        print(f"DEBUG: Create GConnection object with ID {self.id}")
        print(f"DEBUG:        --> name: {self.name}")
        print(f"DEBUG:        --> g_object: {self.g_object}")
        print(f"DEBUG:        --> g_nodes: {self.g_nodes}")
        print(f"DEBUG:        --> max_nodes: {self.max_nodes}")

    def next_id(self):
        GConnection.last_id += 1
        return GConnection.last_id

