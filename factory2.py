#!/usr/bin/env python

import random

#
# Our Shape Objects
#

class Shape:
    pass

class Circle(Shape):
    def draw(self):
        print("Circle.draw")
    def erase(self):
        print("Circle.erase")
    class Factory:
        def create(self):
            return Circle()

class Square(Shape):
    def draw(self):
        print("Square.draw")
    def erase(self):
        print("Square.erase")
    class Factory:
        def create(self):
            return Square()

#
# Our Shape Factory - uses a class variable "factories" and static methods
#

class ShapeFactory:
    factories = {}

    @staticmethod
    def addFactory(id, shapeFactory):
        ShapeFactory.factories[id] = shapeFactory

    @staticmethod
    def createShape(id):
        if not id in ShapeFactory.factories:
            #
            # 1. Build the string composed of object type (e.g. "Circle")
            #    and the method ".Factory()" to get "Circle.Factory()"
            #
            str_to_eval = id + '.Factory()'
            #
            # 2. Evaluate that string to get ref to the Factory class within
            #    the Shape class.
            #
            factory_class = eval(str_to_eval)
            #
            # 3. Finally, we assign the newly-created object ID to
            #    ShapeFactory.factories Dictionary
            #
            #ShapeFactory.factories[id] = factory_class
            ShapeFactory.addFactory(id, factory_class)
            #
            # 4. Call the .create() method on that class to get a new instance
            #    of the Shape object.
            #
        return ShapeFactory.factories[id].create()

#
# Show how we can use the factory
#

#def shapeNameGen(n):
#    types = Shape.__subclasses__()
#    for i in range(n):
#        yield random.choice(types).__name__

#shapes = [ ShapeFactory.createShape(i) for i in shapeNameGen(12)]

shape_names = ['Square', 'Circle', 'Square', 'Circle', 'Circle', 'Square', 'Circle']

print(f"shape_names = {shape_names}")

shapes = []
for shape_name in shape_names:
    shapes.append(ShapeFactory.createShape(shape_name))

#print(f"shapes = {shapes}")

for shape in shapes:
    print(shape)
    shape.draw()
    shape.erase()

