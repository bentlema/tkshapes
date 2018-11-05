

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

    def screen_to_canvas_coords(self, screen_x, screen_y):
        canvas_x = self.gcanvas.canvas.canvasx(screen_x)
        canvas_y = self.gcanvas.canvas.canvasy(screen_y)
        return canvas_x, canvas_y

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
        # TODO: the input and output components would not be draggable.  Same goes for "selectable", so the current
        # TODO: assumption works for now, so I'll leave it until a case comes up where this doesn't work.

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
        #print(f"DEBUG: BEGIN CONNECTION - Button-{event.num} Item: {canvas_item}")
        self._drag_data["item"] = canvas_item
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

        # Find GItem from Canvas Item ID
        g_item = self.get_item_by_id(canvas_item)
        x, y = g_item.center_point()

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
        #print(f"DEBUG: START CONNECTION")
        #print(f"       --> GObject: {from_g_object}")
        #print(f"       -->   GItem: {from_g_item} {connect_from_item}")
        #print(f"       -->   GNode: {from_node_name}")
        #print(f"       -->   Start: {int(self._connection_data['start_x'])} x {int(self._connection_data['start_y'])}")

        x, y = self.screen_to_canvas_coords(event.x, event.y)

        # TODO: we need to check for the closest, but also check for closest that is a GNode, otherwise if there is
        # TODO: another GWire close by, it could find that one instead.  This is less of an issue when the GNode
        # TODO: circle is raised above the GWire, which is what we are doing, so maybe wont worry about it for now.
        connect_to_item = self.gcanvas.canvas.find_closest(x, y)

        if connect_to_item:
            to_g_object = self.gcanvas.get_gobject_by_id(connect_to_item)
        else:
            to_g_object = None

        if to_g_object:
            to_g_item = to_g_object.get_item_by_id(connect_to_item)
        else:
            to_g_item = None

        if to_g_item and to_g_item.connectable_terminator:
            to_node_name = to_g_object.get_node_name_by_g_item(to_g_item)
        else:
            #print(f"DEBUG: GItem is NOT a connection_terminator")
            # reject the GItem
            to_node_name = None

        # TODO: We need to check and enforce max_connections for GNode objects, and
        # TODO: max_nodes for GConnection objects.

        if to_node_name:
            #print(f"DEBUG: END CONNECTION - Button-{event.num}")
            #print(f"       --> GObject: {to_g_object}")
            #print(f"       -->   GItem: {to_g_item} {connect_to_item}")
            #print(f"       -->   GNode: {to_node_name}")
            #print(f"       -->     End: {int(x)} x {int(y)}")

            coords = (
                int(self._connection_data['start_x']),
                int(self._connection_data['start_y']),
                int(x),
                int(y),
            )

            # TODO: add a method to get GObject name, rather than use protected member "_tag" directly
            new_wire_name = from_g_object._tag + "_" + from_node_name + "__to__" + to_g_object._tag + "_" + to_node_name
            #print(f"DEBUG: FINALIZE CONNECTION")
            #print(f"       -->     Coords: {coords}")
            #print(f"       -->       Name: {new_wire_name}")
            new_wire = self.gcanvas.create('GWire', coords, name=new_wire_name)

            new_wire.connect(
                from_g_object.node(from_node_name),
                to_g_object.node(to_node_name)
            )
            new_wire.update()
        else:
            #print(f"DEBUG: END CONNECTION - Button-{event.num}")
            #print(f"       --> Where?")
            pass

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

        x, y = self.screen_to_canvas_coords(event.x, event.y)

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

        x, y = self.screen_to_canvas_coords(event.x, event.y)

        # update status var
        if self.gcanvas.status_var:
            self.gcanvas.status_var.set(f"Dragging {self._tag} at {x}x{y}")

    def on_command_button_press(self, event):
        """ handle Command-Click on a GObject to toggle Selection """

        clicked_item = self.gcanvas.canvas.find_withtag('current')

        if self.selectable:
            self.toggle_selected()
            #print("Item ID {} --> Command-Clicked --> Selected? {}".format(clicked_item, self._selected))
        else:
            #print("Item {} not selectable.".format(clicked_item))
            pass

    def raise_up(self):
        for g_item_name in self._items:
            g_item = self._items[g_item_name]
            g_item.raise_up()
            if g_item.raisable:
                g_item.raise_up()

    def raise_up_neighbors(self):
        if self._nodes:
            for g_node_name in self._nodes:
                g_node = self._nodes[g_node_name]
                for g_conn in g_node.connections:
                    g_conn.g_object.raise_up() # The GWire
                    for neighbor_g_node in g_conn.g_nodes:
                        neighbor_g_node.g_object.raise_up()

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
                self.raise_up_neighbors()
                self.raise_up()

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
        #print(f"DEBUG: Draw GObject {self}")
        pass

    def node(self, name):
        return self._nodes[name]

    def connect(self, node1, node2):
        """ connect one GObject's GNode to another """
        #print(f"DEBUG: GObject.connect():")
        #print(f"DEBUG:      GConnection:  {self.connection} g_object: {self.connection.g_object}")
        #print(f"DEBUG:      GNode1: {node1} id: {node1.id} name: '{node1.name}'")
        #print(f"DEBUG:      GNode2: {node2} id: {node2.id} name: '{node2.name}'")
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
    #def make_undraggable(self):
    #    """ Make the GObject undraggable (immovable) across the canvas """
    #    for i in self._items:
    #        print(f"DEBUG: Setting GItem {i} dragability to False")
    #        self._items[i].draggable = False

    #def make_draggable(self):
    #    """ Make the GObject draggable across the canvas """
    #    for i in self._items:
    #        print(f"DEBUG: Setting GItem {i} dragability to True")
    #        self._items[i].draggable = True

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

