
import tkinter as tk

class AppRootWindow(tk.Frame):
    ''' Create the Tk Application's root window -- root parameter must be the Tk root object '''

    def __init__(self, root, window_width=320, window_height=240):

        # Initialize parent class
        tk.Frame.__init__(self, root)

        # Remember the Tk root window
        self.root = root

        # Set desired initial window dimensions
        self.window_width = window_width
        self.window_height = window_height

        # Get max possible size for our root window
        (self.initial_window_max_width, self.initial_window_max_height) = self.root.maxsize()

        self.window_max_width = self.initial_window_max_width
        self.window_max_height = self.initial_window_max_height

        # Set window maximum size (this seems to help buggy behavior on macOS)
        self.root.maxsize(self.window_max_width, self.window_max_height)

        # Configure window minimum size
        self.root.minsize(320, 240)

        # Debugging
        #print("                 Max size: {}x{}".format(self.window_max_width, self.window_max_height))
        #print("Current window dimentions: {}x{}".format(self.root.winfo_width(), self.root.winfo_height()))
        #print("        Screen dimentions: {}x{}".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        #print("--------------------------------------------------------------------------------")

        # Set default window transparency
        self.root.attributes("-alpha", 0.85)

        # Initialize screen width and height with get_screen_size()
        (self.screen_width, self.screen_height) = self.get_screen_size()

        if self.screen_width < self.initial_window_max_width:
            print("Running on a Multi-Display system...")
            self.multi_display = True
        else:
            print("Running on a Single-Display system...")
            self.multi_display = False

        # Configure initial window position to be the middle of the screen
        self.window_loc_x = int((self.screen_width / 2) - (self.window_width / 2))
        self.window_loc_y = int((self.screen_height / 2) - (self.window_height / 2))

        # The <Configure> event will be triggered when the window is moved or re-sized
        self.root.bind('<Configure>', self.window_update_callback)

        # Initial size and placement of window
        self.update_window_geometry()


    def window_update_callback(self, event):
        #print(event)
        # The primary screen top/left pixel will be at (0,0) so if we are negative, we are probably
        # on the secondary display, or if we are positive greater than the width of our primary display
        # TODO: need to consider that if a secondary display is in use, it could be on either side of
        # TODO: the primary display.  If on the left, we will have negative x values when our window
        # TODO: is positioned on the second display.  If on the right, we will have positive x values
        # TODO: but they will be greater than the screen_width.  If we have triple displaies, we'd have
        # TODO: both scenarios.  It would be nice to write up the tests to determine if we have a 2nd
        # TODO: or 3rd display, and be able to tell which display our window is on.
        # TODO:
        # TODO: We should also test that the main window is fully on one screen or the other before making
        # TODO: decisions about the max window size.
        if self.multi_display:
            if event.x > self.screen_width or event.x < 0:
                if self.status_var:
                    self.status_var.set("We are probably on the SECONDARY display")
            else:
                if self.status_var:
                    self.status_var.set("We are probably on the PRIMARY display")

        #print("                 Max size: {}".format(self.root.maxsize()))
        #print("        Screen dimentions: {}x{}".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        #print("Current window dimentions: {}x{}".format(self.root.winfo_width(), self.root.winfo_height()))
        #print("--------------------------------------------------------------------------------")

    def get_screen_size(self):
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        return((width, height))

    def set_window_max_size(self, width=0, height=0):
        '''
        Configure the maximum window size to be given width and height
        If width and/or height are not given, will base them off of screen width/height
        '''
        if width <= 0:
            self.window_max_width = int(self.screen_width * .99)
        else:
            self.window_max_width = width

        if height <= 0:
            self.window_max_height = int(self.screen_height * .95)
        else:
            self.window_max_height = height

        print("Setting window max size to {}x{}".format(self.window_max_width, self.window_max_height))
        self.root.maxsize(self.window_max_width, self.window_max_height)

    # should we make this a property?
    def set_window_size(self, width, height):
        self.window_width = width
        self.window_height = height

    # should we make this a property?
    def set_window_location(self, x, y):
        self.window_loc_x = x
        self.window_loc_y = y

    # and then make the properties above call this update function when the setters are used
    def update_window_geometry(self):
        ''' set the root window size and position '''
        geometry = "{}x{}+{}+{}".format(self.window_width, self.window_height, self.window_loc_x, self.window_loc_y)
        self.root.geometry(geometry)

    def register_status_var(self, var):
        self.status_var = var