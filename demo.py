#!/usr/bin/env python

import tkinter as tk
import tkinter.ttk as ttk

from tkapp import AppRootWindow
from tkshapes import GCanvas


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

# Register builtin shapes
gcanvas.register_builtins()

# The 'BACKGROUND' name will associate this GObject with the immovable background items
graph_paper = gcanvas.create('GGraphPaper', 0, 0, 10000, 10000, name="BACKGROUND")
graph_paper.set_outline_width(2)
graph_paper.set_active_outline_width(0)
graph_paper.show()

# GObjects are "spawned" into existence by the create() method on the GCanvas
#
# An optional "label" can be added to the GObject for display purposes only.
# The label does not need to be unique, and can contain whitespace.
#
# An optional "name" can be added which will be used in the underlying GItem's
# name_tag, and must be unique.  Using a unique name can be useful in development
# when printing out debug code, you can more easily see what objects you're
# dealing with if they're named something meaningful.

circle1 = gcanvas.create('GOval', 5390, 5100, 100, 100, label="Circle1")
circle1.add_mouse_bindings()
circle1.show()

circle2 = gcanvas.create('GOval', 5360, 5200, 50, 50, label="Circle2")
circle2.add_mouse_bindings()
circle2.show()

circle3 = gcanvas.create('GOval', 5340, 5250, 20, 20, label="Circle3")
circle3.add_mouse_bindings()
circle3.show()

oval1 = gcanvas.create('GOval', 5330, 5300, 20, 30, label="Oval1")
oval1.add_mouse_bindings()
oval1.show()

oval2 = gcanvas.create('GOval', 5330, 5350, 50, 40, label="Oval2")
oval2.add_mouse_bindings()
oval2.show()

oval3 = gcanvas.create('GOval', 5330, 5400, 100, 130, label="Oval3")
oval3.add_mouse_bindings()
oval3.show()

square1 = gcanvas.create('GRect', 5520, 5030, 100, 100, label="Square1")
square1.add_mouse_bindings()
square1.show()

square2 = gcanvas.create('GRect', 5650, 5060, 75, 75, label="Square2")
square2.add_mouse_bindings()
square2.show()

square3 = gcanvas.create('GRect', 5675, 5150, 25, 25, label="Square3")
square3.add_mouse_bindings()
square3.show()

gate1 = gcanvas.create('GBufferGate', 5060, 5040, label="BufferGate1")
gate1.add_mouse_bindings()
gate1.show()

gate2 = gcanvas.create('GNotGate', 5200, 5040, label="NotGate1")
gate2.add_mouse_bindings()
gate2.show()

gate3 = gcanvas.create('GAndGate', 5060, 5140, label="AndGate1")
gate3.add_mouse_bindings()
gate3.show()

gate4 = gcanvas.create('GOrGate', 5053, 5240, label="OrGate1")
gate4.add_mouse_bindings()
gate4.show()

gate5 = gcanvas.create('GXOrGate', 5060, 5340, label="XOrGate1")
gate5.add_mouse_bindings()
gate5.show()

gate6 = gcanvas.create('GNandGate', 5200, 5140, label="NandGate1")
gate6.add_mouse_bindings()
gate6.show()

gate7 = gcanvas.create('GNorGate', 5200, 5240, label="NorGate1")
gate7.add_mouse_bindings()
gate7.show()

gate8 = gcanvas.create('GXNorGate', 5200, 5340, label="XNorGate1")
gate8.add_mouse_bindings()
gate8.show()

logo = gcanvas.create('GPythonLogo', 5500, 5160, label="TwoSnakes")
logo.add_mouse_bindings()
logo.show()

# Print some debug info
gcanvas.known_types()
gcanvas.known_gobjects()

# Start the Tkinter event loop
root.mainloop()

