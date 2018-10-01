
import tkinter as tk
import tkinter.ttk as ttk

class GCanvas(tk.Frame):

    def __init__(self, parent, canvas_width=10000, canvas_height=10000):

        # Initialize parent class
        tk.Frame.__init__(self, parent)

        # Remember the Tk parent window
        self.parent = parent

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

        self.tag = "graph_paper"
        self.bg_color = "#eeffee"
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                     fill=self.bg_color, outline=self.bg_color, tag=self.tag)

        # TODO: Draw a dot off the screen that we will use to keep track of a width and activewidth, which
        # TODO: we will use on all other canvas objects as well.  Actually, we should probably just use
        # TODO: a pair of instance variables, but want to try this first. Actually, NO, we should start to
        # TODO: keep track of the GObjects on the GCanvas in a Dictionary, with the key being the name tag
        # TODO: given when the GObject is created.  Will come back to this...

        self.canvas.create_oval(-100, -100, -100, -100, width=1, activewidth=0, tag="scale_on_zoom_1_0")
        self.canvas.create_oval(-100, -100, -100, -100, width=2, activewidth=2, tag="scale_on_zoom_2_2")
        self.canvas.create_oval(-100, -100, -100, -100, width=5, activewidth=5, tag="scale_on_zoom_5_5")
        self.canvas.create_oval(-100, -100, -100, -100, width=7, activewidth=7, tag="scale_on_zoom_7_7")
        self.canvas.create_oval(-100, -100, -100, -100, width=9, activewidth=9, tag="scale_on_zoom_9_9")
        self.canvas.create_oval(-100, -100, -100, -100, width=2, activewidth=5, tag="scale_on_zoom_2_5")

        # Draw the Graph Paper background.  We draw all of the vertical lines, followed by all of the
        # horizontal lines.  Every 100 pixels (or every 10th line) we draw using a DARKER green, to
        # simulate the classic "Engineer's Graph Paper".  We draw the lines to cover the entire canvas,
        # even those portions that are out of view, as we want to be able to scroll across the entire
        # canvas, and never see any uncovered areas.

        # Creates all vertical lines
        for i in range(0, self.canvas_width, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.canvas.create_line([(i, 0), (i, self.canvas_height)], fill=line_color, tag=self.tag)

        # Creates all horizontal lines
        for i in range(0, self.canvas_height, 10):
            if (i % 100) == 0:
                line_color = "#aaffaa"
            else:
                line_color = "#ccffcc"
            self.canvas.create_line([(0, i), (self.canvas_width, i)], fill=line_color, tag=self.tag)

        # Tag all graph_paper canvas objects with scale_on_zoom_1_0 as all lines start out with
        # a width of 1 and we never use activewidth, so active width is 0
        self.canvas.addtag_withtag("scale_on_zoom_1_0", "graph_paper")

        # Ensure that all canvas objects tagged as 'graph_paper' are pushed down to the lowest layer,
        # as all subsequently-created objects will be draggable across the top of the canvas
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
        # print("canvas size = {}x{}".format(w, h))
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
        # the background graph paper, has been scaled up or down, and since it's that background that
        # determines our scroll region, we have to adjust it every time we zoom in or out.
        self.canvas.configure(scrollregion=self.canvas.bbox(self.tag))

        # Scale the line width and active width on all canvas items too
        # For items with initial line width 1, and active width 0, they should be tagged scale_on_zoom_1_0
        # For items with initial line width 2, and active width 5, they should be tagged scale_on_zoom_2_5

        for tag in ("scale_on_zoom_1_0",
                    "scale_on_zoom_2_2",
                    "scale_on_zoom_5_5",
                    "scale_on_zoom_7_7",
                    "scale_on_zoom_9_9",
                    "scale_on_zoom_2_5"):
            current_width = self.canvas.itemcget(tag, "width")
            current_activewidth = self.canvas.itemcget(tag, "activewidth")
            new_width = float(current_width) * sf
            new_activewidth = float(current_activewidth) * sf
            self.canvas.itemconfigure(tag, width=new_width)
            self.canvas.itemconfigure(tag, activewidth=new_activewidth)

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

    def on_button_motion(self, event):
        # Convert window coordinates into canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        # Handle resize of the rectangular selection box - Delete and re-draw the selection box
        self.canvas.delete("selection_box")
        self.canvas.create_rectangle(self._drag_data["start_x"], self._drag_data["start_y"], x, y, tags="selection_box")


