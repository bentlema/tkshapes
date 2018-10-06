#!/usr/bin/env python

import tkinter as tk
import tkinter.ttk as ttk

from graphics import (
    AppRootWindow,
    GCanvas,
    GGraphPaper,
    GRect,
    GOval,
    GBufferGate,
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
graph_paper = GGraphPaper(0, 0, 10000, 10000, name_tag="BACKGROUND")
graph_paper.set_outline_width(2)
graph_paper.set_active_outline_width(0)
graph_paper.add_to(gcanvas)

rectanble = GRect(5200, 5200, 100, 200, name_tag="Rectangle")
rectanble.add_to(gcanvas)
rectanble.make_draggable()

circle = GOval(5400, 5200, 100, 100, name_tag="Circle")
circle.add_to(gcanvas)
circle.make_draggable()

buffer_gate = GBufferGate(5100, 5100, name_tag="BufferGate")
buffer_gate.add_to(gcanvas)
buffer_gate.make_draggable()

root.mainloop()

