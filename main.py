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
    GBufferGate,
    GCompound,
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

# Using the 'BACKGROUND' name_tag will associate this GObject with the immovable background items
# TODO: using the 'background' tag requires special knowledge about the implementation of the GCanvas, so I
# TODO: do not like that, but will come back to this later, and make a method that registers a GObject as
# TODO: a background component...
graph_paper = GGraphPaper(0, 0, 10000, 10000, name_tag="BACKGROUND")
graph_paper.set_outline_width(2)
graph_paper.set_active_outline_width(0)
graph_paper.add_to(gcanvas)

bar = GRect(5200, 5200, 100, 200, name_tag="Bar")
bar.add_to(gcanvas)
bar.make_draggable()

cir = GOval(5400, 5200, 100, 100, name_tag="Cir")
cir.add_to(gcanvas)
cir.make_draggable()

gate = GBufferGate(5100, 5100, name_tag="BufferGateMain")
gate.add_to(gcanvas)
gate.make_draggable()

#output_cir = GOval(5166, 5123, 10, 10, name_tag="BufferGateOutputCir")
#output_cir.add_to(gcanvas)
#output_cir.make_draggable()

#output_line = GLine(5158, 5128, 10, name_tag="BufferGateOutputLine")
#output_line.add_to(gcanvas)
#output_line.make_draggable()

#input_cir = GOval(5080, 5123, 10, 10, name_tag="BufferGateInputCir")
#input_cir.add_to(gcanvas)
#input_cir.make_draggable()

#input_line = GLine(5090, 5128, 10, name_tag="BufferGateInputLine")
#input_line.add_to(gcanvas)
#input_line.make_draggable()

# Not done -- doesn't work
#compound = GCompound(5000, 5000, name_tag="BufferGateComplete")
#compound.add_part(gate)
#compound.add_part(output_cir)
#compound.add_part(output_line)
#compound.add_part(input_cir)
#compound.add_part(input_line)
#compound.add_to(gcanvas)
#compound.make_draggable()

root.mainloop()

