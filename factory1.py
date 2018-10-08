#!/usr/bin/env python

import random

class Shape(object):
    # Create based on class name:

    @staticmethod
    def factory(type):
        #return eval(type + "()")
        if type == "Circle": return Circle()
        if type == "Square": return Square()
        assert 0, "Bad shape creation: " + type

class Circle(Shape):
    def draw(self):
        print("Circle.draw")
    def erase(self):
        print("Circle.erase")

class Square(Shape):
    def draw(self):
        print("Square.draw")
    def erase(self):
        print("Square.erase")

shape_names = ['Square', 'Circle', 'Square', 'Circle', 'Circle', 'Square', 'Circle']

shapes = [ Shape.factory(name) for name in shape_names ]

for shape in shapes:
    print(shape)
    shape.draw()
    shape.erase()

