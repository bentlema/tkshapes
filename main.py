#!/usr/bin/env python

import tkinter as tk
import tkinter.ttk as ttk

from graphics import AppRootWindow, GCanvas, BufferGate, GRect

root = tk.Tk()

root_window = AppRootWindow(root, window_width=800, window_height=600)
root_window.pack(fill="both", expand=True)

statusbar_frame = tk.Frame(root_window)
statusbar_frame.pack(side="bottom", fill="x", expand=True, anchor="s")

statusbar_label = ttk.Label(statusbar_frame, text="This is the statusbar text", anchor="w")
statusbar_label.pack(side="left", fill="both", expand=True)

gcanvas = GCanvas(root_window, canvas_width=10000, canvas_height=10000)
gcanvas.pack(fill="both", expand=True)

foo = BufferGate(gcanvas, "Foo", 5100, 5100)

#foo = BufferGate("Foo", 5100, 5100)
#gcanvas.add(foo)

bar = GRect(gcanvas, "Bar", 5200, 5200)

root.mainloop()

