
import tkinter as tk
import tkinter.ttk as ttk

class GCanvas(tk.Frame):

    def __init__(self, parent, canvas_width=10000, canvas_height=10000):

        # Initialize parent class
        tk.Frame.__init__(self, parent)

        # Remember my Tk parent window/frame
        self.parent = parent

        # Remember the GObjects that are on this GCanvas
        # The GCanvas is an abstraction on top of the tkinter Canvas, and GObjects are an abstraction on top of
        # the canvas' items.  For each GObject created on the GCanvas, there could me one or more items rendered.
        # Since each GObject has a unique name_tag, we will use a Dictionary keyed off of that to store them
        self.gobjects = {}

        # Where to send status messages
        self.status_var = None

        # Remember our canvas dimensions (will change when we zoom in/out)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        # Create our Tk Canvas
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height,
                             borderwidth=0, highlightthickness=0)

        # Draw and tag a background rectangle which will give us the ability to scroll the canvas only when
        # clicking and dragging on the background, but will not drag when we click on another object on the
        # canvas (such as a gate or wire) as those objects will be tagged with different names. We bind the
        # tag of the background objects to the click/drag events.  See below scroll_start() and scroll_move()

        self.tag = "background"
        self.bg_color = "#ff0000"
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                     fill=self.bg_color, outline=self.bg_color, tag=self.tag)

        # Ensure the background rectangle is lowered to the lowest possible layer in the stacking order
        self.canvas.tag_lower(self.tag)

        # Create the scrollbars and associate one with the canvas
        self.xsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview, style='TScrollbar')
        self.ysb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview, style='TScrollbar')

        # When the canvas is moved by click and drag, we also update the scrollbars to match
        self.canvas.config(yscrollcommand=self.ysb.set)
        self.canvas.config(xscrollcommand=self.xsb.set)

        # Limit scrolling of the canvas to the area we've drawn on.  This prevents us from scrolling
        # past the edges of the graph paper and exposing blank canvas space
        self.canvas.config(scrollregion=self.canvas.bbox(self.tag))

        # Control how fast you can scroll.  The larger the number, the faster the scrolling, but less smooth
        self.canvas.config(xscrollincrement=1, yscrollincrement=1)

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Allow the canvas (in grid row 0, col 0) to stretch (grow/shrink) with window/frame size changes
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Bindings for click and drag panning/scrolling the canvas
        self.canvas.tag_bind(self.tag, "<Control-ButtonPress-1>", self.scroll_start)
        self.canvas.tag_bind(self.tag, "<Control-B1-Motion>", self.scroll_move)

        # Bindings for panning/scrolling the canvas.  May use 2-finger swipe gesture on the trackpad
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

        # Bindings for Zooming in/out
        self.canvas.bind("<Control-MouseWheel>", self.on_zoom)

        # this data is used to keep track of a canvas object being dragged
        self._drag_data = {
            "x": 0,
            "y": 0,
            "start_x": 0,
            "start_y": 0,
            "end_x": 0,
            "end_y": 0}

        # Bindings for selecting groups of canvas items with a rectangular selection box
        self.canvas.tag_bind(self.tag, "<ButtonPress-1>", self.on_button_press)
        self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.on_button_release)
        self.canvas.tag_bind(self.tag, "<B1-Motion>", self.on_button_motion)

        # Scroll the canvas to the center
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)

    def add(self, name_tag, gobject):
        self.gobjects[name_tag] = gobject
        print(f"GCanvas knows about {len(self.gobjects)} GObjects")
        print(f"     --> GCanvas knows about {self.gobjects}")

    # Setup Click-and-Drag to pan the canvas.  Tkinter canvas provides scan_mark() and scan_dragto()
    # to assist in click-and-drag events.  We use these to pan/scroll the canvas.

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    # Setup Two-Finger Swipe gesture to pan/scroll the canvas both horizontally and vertically.
    # Note: both horizontal and vertical scrolling arrive via MouseWheel events, and are distinguished
    # by the state attribute.
    #
    #     If event.state == 1, the Shift key is pressed, and we apply horizontal scrolling.
    #     If event.state == 0, the Shift key is NOT pressed, and we apply vertical scrolling.

    def on_mousewheel(self, event):
        # On the Trackpad Horizontal_Swipe looks like SHIFT + Vertical_Swipe
        shift = (event.state & 0x1) != 0
        if shift:
            self.canvas.xview_scroll(-1 * event.delta, "units")
        else:
            self.canvas.yview_scroll(-1 * event.delta, "units")

    def on_zoom(self, event):
        # We scale the canvas to simulate a zoom in/out
        # We scale about the current location of the pointer
        # print("\n\nmouse pointer {},{}".format(event.x, event.y))
        sf = 1.0
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        #print("canvas size = {}x{}".format(w, h))
        (x0, y0, x1, y1) = self.canvas.bbox(self.tag)
        # print("bbox size = {}".format(self.canvas.bbox(self.tag)))
        # print("x0 - x1 = {}".format(x1 - x0))
        # print("y0 - y1 = {}".format(y1 - y0))

        # convert from screen coordinates to canvas coordinates (we want to scale relative to canvas coordinates)
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        # Zoom In
        if (event.delta > 0) and ((y1 - y0) <= 50000):
            sf = 1.1  # Just a tad more than 1
            self.canvas.scale("all", cx, cy, sf, sf)

        # Zoom Out
        elif (event.delta < 0) and ((x1 - x0) - 1000 >= w):
            sf = 0.9  # Just a tad less than 1
            self.canvas.scale("all", cx, cy, sf, sf)

        # Adjust the scroll region based on new canvas background size.  All canvas objects, including
        # the background, have been scaled up or down, and since it's that background that
        # determines our scroll region, we have to adjust it every time we zoom in or out.
        self.canvas.configure(scrollregion=self.canvas.bbox(self.tag))

        # Scale the outline width and active outline width on all canvas items too so they appear to change size
        # at the same rate as the shapes they are depicting.  For example, as we Zoom OUT, a Circle scales IN, the
        # width of the line drawn to show the circle on the canvas also gets thiner.  If we Zoom IN, the line drawn
        # would be rendered thicker.  This complets the illusion that we are Zooming IN/OUT even though we are just
        # scaling up or scaling down the size of objects.
        #
        # for each GObject, call the scale method to scale both the object itself, and its outline, and
        # active outline values.  We can scale all items on the canvas as above (all at the same time) but this
        # is only useful for Zooming IN/OUT.  GObjects should also know how to scale themselves, in case our
        # application wants to be able to re-size an individual GObject.
        for gobject in self.gobjects.values():
            gobject.scale(sf)

    def on_button_press(self, event):
        # Clear any current selection first
        self.canvas.dtag("all", "selected")
        # Convert window coordinates into canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Beginning of selection box - record the initial click
        print("Click   ({},{})".format(x, y))
        # Save the location of the initial click
        self._drag_data["start_x"] = x
        self._drag_data["start_y"] = y
        # Create the selection rectangle
        self.canvas.create_rectangle(x, y, x, y, tags="selection_box")

        if self.status_var:
            self.status_var.set("Starting selection...")

    def on_button_release(self, event):
        # Convert window coordinates into canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # End of selection box - record the coordinates of the button release
        print("Release ({},{})".format(x, y))
        self._drag_data["end_x"] = x
        self._drag_data["end_y"] = y
        self.canvas.delete("selection_box")
        # for all items within the selection box, add the "selected" tag, and then trigger the virtual <<Selection>> event
        self.canvas.addtag_enclosed("selected", self._drag_data["start_x"], self._drag_data["start_y"],
                                    self._drag_data["end_x"], self._drag_data["end_y"])
        self.canvas.event_generate("<<Selection>>")

        if self.status_var:
            self.status_var.set("Items selected.")

    def on_button_motion(self, event):
        # Convert window coordinates into canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Handle resize of the rectangular selection box - Delete and re-draw the selection box
        self.canvas.delete("selection_box")
        self.canvas.create_rectangle(self._drag_data["start_x"], self._drag_data["start_y"], x, y, tags="selection_box")

        if self.status_var:
            self.status_var.set("Dragging Selection Box...")

    def register_status_var(self, var):
        self.status_var = var


