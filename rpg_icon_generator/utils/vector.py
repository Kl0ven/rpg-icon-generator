import copy
import math

class Vector:
    def __init__(self, x=None, y=None):
        self.x = 0
        self.y = 0
        if y is None:
            if x is not None:
                self.x = x.x
                self.y = x.y
        else:
            self.x = x
            self.y = y

    def __str__(self):
        return "Vector(x: {}, y: {})".format(self.x, self.y)

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length
        return self

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def lengthSq(self):
        return self.x * self.x + self.y * self.y

    def distanceTo(self, x, y):
        return math.sqrt(self.distanceToSq(x, y))

    def distanceToSq(self, x, y=None):
        if y is None:
            dx = self.x - x.x
            dy = self.y - x.y
        else:
            dx = self.x - x
            dy = self.y - y
        return dx * dx + dy * dy

    def addVector(self, v):
        self.x += v.x
        self.y += v.y
        return self

    def lerpTo(self, v, t):
        self.x = (v.x - self.x) * t + self.x
        self.y = (v.y - self.y) * t + self.y
        return self

    def multiplyScalar(self, v):
        self.x *= v
        self.y *= v
        return self

    def dotProduct(self, x, y=None):
        if y is None:
            return self.x * x.x + self.y * x.y
        else:
            return self.x * x + self.y * y

    def set(self, x, y=None):
        if y is None:
            self.x = x.x
            self.y = x.y
        else:
            self.x = x
            self.y = y
        return self

    def copy(self):
        return copy.deepcopy(self)

    def to_coord(self):
        return (self.x, self.y)
