#!/usr/bin/env python

class GObject:

    @staticmethod
    def factory(a_class, *args, **kwargs):
        return a_class(*args, **kwargs)


class GRectangle(GObject):

    def __init__(self):
        print("Init GRectangle.")

    def add(self):
        print("Adding GRectangle.")


class GOval(GObject):

    def __init__(self):
        print("Init GOval.")

    def add(self):
        print("Adding GOval.")

# Create object using factory.
obj = GObject.factory(GRectangle)
obj.add()

# Create another object using factory.
obj = GObject.factory(GOval)
obj.add()

