#!/usr/bin/env python

class GCanvas:

    def __init__(self):
        self.gobjects = {}
        self.gobject_types = {}
        print("GCanvas has been initialized")

    def register_gobject(self, name, a_class):
        self.gobject_types[name] = a_class
        print(f"Registered {name} which is a {a_class}")

    def known_types(self):
        print("Known GObject types:")
        print(f"     Count = {len(self.gobject_types)}")
        for t in self.gobject_types.keys():
            print(f"     type = {t}")

    def known_gobjects(self):
        print("Known GObjects:")
        print(f"     Count = {len(self.gobjects)}")
        for g in self.gobjects.keys():
            print(f"     GObject = {g}")

    def create(self, a_type, name):
        obj = GObject.factory(self.gobject_types[a_type], name)
        print(f"     {name} = {obj}")
        # GCanvas will remember what GObjects it holds
        self.gobjects[name] = obj
        return obj


class GObject:

    @staticmethod
    def factory(a_class, *args, **kwargs):
        return a_class(*args, **kwargs)


class GRectangle(GObject):

    def __init__(self, *args, **kwargs):
        print("Init GRectangle.")

    def add(self):
        print("Adding GRectangle.")


class GOval(GObject):

    def __init__(self, *args, **kwargs):
        print("Init GOval.")

    def add(self):
        print("Adding GOval.")


gcanvas = GCanvas()
gcanvas.known_types()
gcanvas.known_gobjects()
gcanvas.register_gobject('GRectangle', GRectangle)
gcanvas.register_gobject('GOval', GOval)
gcanvas.known_types()
gcanvas.known_gobjects()

oval1 = gcanvas.create('GOval', name='MyFirstOval')
oval1.add()

rect1 = gcanvas.create('GRectangle', name='MyFirstRectangle')
rect1.add()

rect2 = gcanvas.create('GRectangle', name='MySecondRectangle')
rect2.add()

oval2 = gcanvas.create('GOval', name='MySecondOval')
oval2.add()

gcanvas.known_gobjects()

