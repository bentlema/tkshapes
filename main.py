#!/usr/bin/env python

from tkinter import *
from graphics import GCanvas, BufferGate, GRect

root = Tk()

gcanvas = GCanvas(root,
                  window_width=800,
                  window_height=600,
                  canvas_width=10000,
                  canvas_height=10000
                 )

foo = BufferGate(gcanvas, "Foo", 5100, 5100)

bar = GRect(gcanvas, "Bar", 5200, 5200)

root.mainloop()

