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

hand_coords = (
    4962, 2086, 5571, 3199, 6061, 4158, 6449, 5009, 6271, 5344, 5932, 5127, 5689, 4692,
    5398, 4240, 5005, 4339, 4860, 5018, 4817, 5697, 4935, 6638, 4957, 7335, 4968, 7833,
    4898, 8403, 4779, 8557, 4618, 8502, 4575, 8222, 4569, 7706, 4564, 7362, 4483, 6783,
    4375, 6122, 4181, 5950, 4052, 6421, 3961, 7145, 3815, 7733, 3691, 8620, 3514, 8855,
    3298, 8665, 3347, 8176, 3487, 7443, 3546, 6882, 3724, 5860, 3605, 5860, 3390, 6412,
    3142, 7018, 2798, 8113, 2722, 8158, 2561, 8086, 2496, 7869, 2561, 7543, 2873, 6566,
    2970, 6222, 3228, 5371, 3126, 5308, 2884, 5579, 2518, 6267, 2313, 6575, 2151, 6566,
    2130, 6213, 2351, 5724, 2507, 5353, 2894, 4611, 2991, 4204, 3061, 3633, 3131, 3190,
    3239, 2647, 3363, 2357, 3562, 2176,
)

polygon1_coords = [(x // 5) + 3800 for x in hand_coords]
polygon1 = gcanvas.create('GPolygon', coords=polygon1_coords, label="Polygon1")
polygon1.add_mouse_bindings()
polygon1.show()

bulb1 = gcanvas.create('GLightBulb', 5210, 5500, label="LightBulb1")
bulb1.add_mouse_bindings()
bulb1.show()

#
# There are two options for servicing events for clickable objects.
# 1) handling the virtual event <<MyButtonClick>>
# 2) registering one or more callbacks
#
# If you're handling the operation of a toggle switch (or some other
# multi-state GObject, you'll likely be calling a method such as toggle()
# when events come in, but you want to be sure to not handle the event twice.
# For example, if you're using boch callbacks and event handles, you wouldn't
# want both to issue a g_object.toggle(), otherwise you'd end up canceling
# out the event.
#
# The callback protocol may change, but for now I'm just passing a ref to the
# GObject that was involved.  The event-handler method works the normal way,
# with the event object being passed in to the handler.
#
# The order of a callback vs an event handler being called depends on
# the order in which the binding was made.  Since the GObject binding is always
# made first (within the GObject __init__(), all of the registered callbacks
# will be executed first (before any event handlers defined below.)

def toggle_switch_callback(g_object):
    print("------------------------------------------------------------------------------")
    if g_object.state:
        state = "ON"
    else:
        state = "OFF"
    print(f"DEBUG: toggle_switch_callback(): {g_object.label} is {state}")

def clicked_event_handler(event):

    print("------------------------------------------------------------------------------")

    canvas_item = event.widget.find_withtag('current')
    print(f"DEBUG: canvas_item = {canvas_item}")

    g_item = gcanvas.get_item_by_id(canvas_item)
    print(f"DEBUG: GItem = {g_item}")

    g_object = gcanvas.get_gobject_by_id((g_item.item,))
    print(f"DEBUG: GObject = {g_object}, label = {g_object.label}, state = {g_object.state}")

    # What type of GObject was clicked?
    # TODO: should we add a GObject "type" category, rather than using label???
    # TODO: (we need some way to distinguish between different object types that
    # TODO: have been clicked, as each one may be handled differently.)
    if g_object.label.startswith("ToggleSwitch"):
        g_object.toggle()
        if g_object.state:
            state = "ON"
        else:
            state = "OFF"
        print(f"DEBUG: clicked_event_handler(): {g_object.label} is {state}")

gcanvas.canvas.bind("<<MyButtonClick>>", clicked_event_handler, "+")

switch1 = gcanvas.create('GToggleSwitch', 5060, 5420, label="ToggleSwitch1")
switch1.add_mouse_bindings()
switch1.show()
#switch1.register_callback(toggle_switch_callback)

switch2 = gcanvas.create('GToggleSwitch', 5060, 5460, label="ToggleSwitch2")
switch2.add_mouse_bindings()
switch2.show()
#switch2.register_callback(toggle_switch_callback)

# Print some debug info
gcanvas.known_types()
gcanvas.known_gobjects()

# Start the Tkinter event loop
root.mainloop()

