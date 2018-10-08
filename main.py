#!/usr/bin/env python

import tkinter as tk
import tkinter.ttk as ttk

from graphics import (
    AppRootWindow,
    GCanvas,
    GGraphPaper,
    GLine,
    GRect,
    GOval,
    GBufferGateBody,
)

root = tk.Tk()

status_text = tk.StringVar()
status_text.set("This is the statusbar text")

root_window = AppRootWindow(root, window_width=800, window_height=600)
root_window.pack(fill="both", expand=True)
root_window.register_status_var(status_text)

statusbar_frame = tk.Frame(root_window)
statusbar_frame.pack(side="bottom", fill="x", expand=True, anchor="s")

statusbar_label = ttk.Label(statusbar_frame, textvariable=status_text, anchor="w")
statusbar_label.pack(side="left", fill="both", expand=True)

gcanvas = GCanvas(root_window, canvas_width=10000, canvas_height=10000)
gcanvas.pack(fill="both", expand=True)
gcanvas.register_status_var(status_text)

# The 'BACKGROUND' name_tag will associate this GObject with the immovable background items
#graph_paper = GGraphPaper(0, 0, 10000, 10000, name_tag="BACKGROUND")
#graph_paper.set_outline_width(2)
#graph_paper.set_active_outline_width(0)
#graph_paper.add_to(gcanvas)

#rectangle = GRect(5200, 5200, 100, 200, name_tag="Rectangle")
#rectangle.add_to(gcanvas)
#rectangle.make_draggable()

#circle = GOval(5400, 5200, 100, 100, name_tag="Circle")
#circle.add_to(gcanvas)
#circle.make_draggable()

#buffer_gate_body = GBufferGateBody(5100, 5100, name_tag="BufferGateBody")
#buffer_gate_body.add_to(gcanvas)
#buffer_gate_body.make_draggable()

#buffer_gate_input_line = GLine(5090, 5128, 10, name_tag="BufferGateInputLine")
#buffer_gate_input_line.add_to(gcanvas)

#buffer_gate_input_point = GOval(5080, 5123, 10, 10, name_tag="BufferGateInputPoint")
#buffer_gate_input_point.add_to(gcanvas)

#buffer_gate_output_line = GLine(5158, 5128, 10, name_tag="BufferGateOutputLine")
#buffer_gate_output_line.add_to(gcanvas)

#buffer_gate_output_point = GOval(5168, 5123, 10, 10, name_tag="BufferGateOutputPoint")
#buffer_gate_output_point.add_to(gcanvas)

#compound = GCompound(5000, 5000, name_tag="BufferGateComplete")
#compound.add_part(buffer_gate_body)
#compound.add_part(buffer_gate_input_line)
#compound.add_part(buffer_gate_input_point)
#compound.add_part(buffer_gate_output_line)
#compound.add_part(buffer_gate_output_point)
#compound.add_to(gcanvas)
#buffer_gate_body.make_draggable()


#
# We are completely re-doing the GObject, and GCompound.  Instead we will have a GObject and GItem.
# The GObject will be made up of GItems.  They will each have their own interfaces, which is
# unlike what I was trying to do with GObject and GCompound, which shared the same interface.
# So what we'll end up with is a GCanvas that contains GObjects that contains GItems
#
# The various GObject shapes will be defined in the GObject class, and then "registered" with the
# GCanvas so the GCanvas knows all of the valid kinds of shapes we can create on the canvas.
# Then we can call the new method like this:
gcanvas.register_gobject('GGraphPaper', GGraphPaper)
gcanvas.register_gobject('GRect', GRect)
gcanvas.register_gobject('GOval', GOval)

# The 'BACKGROUND' name will associate this GObject with the immovable background items
graph_paper = gcanvas.create('GGraphPaper', 0, 0, 10000, 10000, name="BACKGROUND")
graph_paper.set_outline_width(2)
graph_paper.set_active_outline_width(0)
graph_paper.add_mouse_bindings()
graph_paper.show()

# GObjects are "spawned" into existence by the create() method on the GCanvas
# The name passed in must be unique, and is used to remember the object on the GCanvas
rectangle = gcanvas.create('GRect', 5200, 5200, 100, 200, name='MyFirstRectangle')

# This should be made into a property
rectangle.make_draggable()

# This should probably be moved into the GCanvas.create() but not sure yet
rectangle.add_mouse_bindings()

# We now have a handle to the 'Rectangle' GObject.  The argument is an arbitrary name, but
# obviously should make sense describing what the GObject is.  Later, we will define other
# more complex GObjects  such as 'AND_Gate', 'OR_Gate', 'Inverter', etc.
#
# We've not provided any dimensions, or location, or colors, etc., for our GObject, so...

# location is a property.  This specifies the x,y coordinates.
#rectangle.location = (5200, 5200)

# dimensions is a property.  This specifies a 100x200 size rectangle.
#rectangle.dimensions = (100, 200)

# draggable is a property.  This says that we are able to click-and-drag the GObject on the GCanvas.
# Note:  the individual GItems making up the GObject will have to define if they accept a click-drag
# or not.  We can accomplish this by setting the 'draggable' tag on those parts (items) that can be
# clicked for a click-and-drag operation.  For example, on an 'AND_Gate', we want to be able to drag
# it only when clicking/holding/dragging on the main body of the gate.  If we click/hold and attempt
# to drag one of the inputs or outputs, nothing would/should happen.
#rectangle.draggable = True

# show the rectangle GObject on the GCanvas. (default is 'hidden')
rectangle.show()

# Let's add another GObject
circle = gcanvas.create('GOval', 5400, 5200, 100, 100, name="Circle")
circle.make_draggable()
circle.add_mouse_bindings()
circle.show()

# Let's add another GObject
square = gcanvas.create('GRect', 5600, 5200, 100, 100, name="MySquare")
square.make_draggable()
square.add_mouse_bindings()
square.show()

# Print some debug info
gcanvas.known_types()
gcanvas.known_gobjects()

# Start the Tkinter event loop
root.mainloop()

