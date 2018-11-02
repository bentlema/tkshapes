Tkinter Canvas Shapes
=====================

**Note:** This is a Python 3.6+ module.

The tkshapes module adds a GCanvas widget which can contain
user-configurable shapes. The GCanvas widget supports the standard Tk
canvas shapes, as well as some others useful in diagrams. (Not all
implemented yet.)

-  GObjects can be constructed from GItems
-  GObjects are displayed on the GCanvas
-  GObjects can be dragged around individually, or selected and dragged
   together
-  GObjects can have GNodes
-  GNodes can be connected by a GConnection (visualized by a GWire)

Controls
--------

The GCanvas Keyboard and Mouse controls are as follows:

-  Control + MouseClickHold-and-Drag or Two-finger swipe to Pan the
   canvas
-  Control + MouseWheel or Control + Two-finger Vertical swipe to Zoom
   In/Out
-  Click-Drag a single shape to move it around on the canvas
-  Command + Click to toggle selection of a single shape

-  Click-Drag on the canvas to mark out a Selection Box

   -  Selected shapes can highlight themselves if configured to do so
      (default)
   -  Click-Drag one of the selected shapes to move them all together
   -  Click anywhere on the canvas to de-select all shapes
   -  Command + Click individual shapes to add/remove shapes from the
      selected set (toggle)

-  To make a connection between two “Connectable” shapes:

   -  Click and Hold on an “Output” Node of a shape (such as one of the
      Logic Gates in the Demo)
   -  Begin to Drag and a wire will appear
   -  Drag the wire to an “Input” Node of another shape and release to
      complete the connection

Dependancies
------------

Create your Python 3.6+ virtual environment

::

   python3.6 -m venv env

Activate your virtual env

::

   source env/bin/activate

Install tkapp (The demo.py depends on the tkapp module.)

::

   pip install tkapp

Alpha - In-Development
----------------------

This library is being developed so that I can use it to build a Digital
Logic Simulator app. I wasn’t able to find a Tkinter library that did
what I need, so decided to try and write one from scratch.

At this time, the only documentation is this README, the code itself, as
well as a demo.py which shows the basic usage.

I’m developing and testing **ONLY** on macOS.

Known Issues
------------

-  when the Tkinter window is put in full-screen mode using the
   full-screen green dot button at the top left of the window, mouse
   position is incorrectly calculated. You’ll notice that the calculated
   mouse position on the GCanvas is slightly off. This appears to be a
   Tkinter bug, but I’m not 100% sure. Instead of using full-screen
   mode, you may click Option-GreenDot to maximize the window to use the
   full screen without actually entering full-screen mode.

