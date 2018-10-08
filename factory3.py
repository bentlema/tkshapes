#!/usr/bin/env python

class Car(object):

    @staticmethod
    def factory(type):
        if type == "Racecar":
            return Racecar()
        if type == "Van":
            return Van()
        raise AssertionError("Bad car creation: " + type)

class Racecar(Car):
    def drive(self): print("Racecar driving.")

class Van(Car):
    def drive(self): print("Van driving.")

# Create object using factory.
obj = Car.factory("Racecar")
obj.drive()

# Create another object using factory.
obj = Car.factory("Van")
obj.drive()
