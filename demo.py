#!/usr/bin/env python

import tkinter as tk
import tkinter.ttk as ttk

from tkapp import AppRootWindow

from tkshapes import (
    GCanvas,
    GGraphPaper,
    GRect,
    GOval,
    GBufferGate,
    GNotGate,
    GAndGate,
    GOrGate,
    GXOrGate,
    GPythonLogo,
)

root = tk.Tk()

root.title("This is the title for the root window")

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

# The various GObject shapes will be defined in the GObject class, and then "registered" with the
# GCanvas so the GCanvas knows all of the valid kinds of shapes we can create on the canvas.
# Then we can call the new method like this:
gcanvas.register_gobject('GGraphPaper', GGraphPaper)
gcanvas.register_gobject('GRect', GRect)
gcanvas.register_gobject('GOval', GOval)
gcanvas.register_gobject('GBufferGate', GBufferGate)
gcanvas.register_gobject('GNotGate', GNotGate)
gcanvas.register_gobject('GAndGate', GAndGate)
gcanvas.register_gobject('GOrGate', GOrGate)
gcanvas.register_gobject('GXOrGate', GXOrGate)
gcanvas.register_gobject('GPythonLogo', GPythonLogo)

# The 'BACKGROUND' name will associate this GObject with the immovable background items
graph_paper = gcanvas.create('GGraphPaper', 0, 0, 10000, 10000, name="BACKGROUND")
graph_paper.set_outline_width(2)
graph_paper.set_active_outline_width(0)
# I dont think we need any of these bindings on the background
#graph_paper.add_mouse_bindings()
graph_paper.show()

# GObjects are "spawned" into existence by the create() method on the GCanvas
# The name passed in must be unique, and is used to remember the object on the GCanvas
#
# TODO: Currently nothing enforces a unique name, and if the programmer uses an already-used
# TODO: name, the generated GObjects will move together on the canvas.  This is not intended
# TODO: to be used as a feature, and eventually I'll get rid of the manual setting of the
# TODO: name, and a randomly-generated ID will be used.  I may still implement the idea
# TODO: of a label, which could be used for display only, but we want to hide the implementation
# TODO: details of how the name is currently used as an underlying canvas item tag.

circle1 = gcanvas.create('GOval', 5260, 5100, 100, 100, name="Circle1")
circle1.add_mouse_bindings()
circle1.show()

circle2 = gcanvas.create('GOval', 5230, 5200, 50, 50, name="Circle2")
circle2.add_mouse_bindings()
circle2.show()

circle3 = gcanvas.create('GOval', 5210, 5250, 20, 20, name="Circle3")
circle3.add_mouse_bindings()
circle3.show()

oval1 = gcanvas.create('GOval', 5200, 5300, 20, 30, name="Oval1")
oval1.add_mouse_bindings()
oval1.show()

oval2 = gcanvas.create('GOval', 5200, 5350, 50, 40, name="Oval2")
oval2.add_mouse_bindings()
oval2.show()

oval3 = gcanvas.create('GOval', 5200, 5400, 100, 130, name="Oval3")
oval3.add_mouse_bindings()
oval3.show()

square1 = gcanvas.create('GRect', 5600, 5040, 100, 100, name="Square1")
square1.add_mouse_bindings()
square1.show()

square2 = gcanvas.create('GRect', 5650, 5160, 75, 75, name="Square2")
square2.add_mouse_bindings()
square2.show()

square3 = gcanvas.create('GRect', 5675, 5250, 25, 25, name="Square3")
square3.add_mouse_bindings()
square3.show()

gate1 = gcanvas.create('GBufferGate', 5060, 5040, name="BufferGate1")
gate1.add_mouse_bindings()
gate1.show()

gate2 = gcanvas.create('GNotGate', 5200, 5040, name="NotGate1")
gate2.add_mouse_bindings()
gate2.show()

gate3 = gcanvas.create('GAndGate', 5060, 5140, name="AndGate1")
gate3.add_mouse_bindings()
gate3.show()

gate4 = gcanvas.create('GOrGate', 5053, 5240, name="OrGate1")
gate4.add_mouse_bindings()
gate4.show()

gate5 = gcanvas.create('GXOrGate', 5060, 5340, name="XOrGate1")
gate5.add_mouse_bindings()
gate5.show()

logo = gcanvas.create('GPythonLogo', 5400, 5200, name="TwoSnakes")
logo.add_mouse_bindings()
logo.show()

# Print some debug info
gcanvas.known_types()
gcanvas.known_gobjects()

# Start the Tkinter event loop
root.mainloop()

