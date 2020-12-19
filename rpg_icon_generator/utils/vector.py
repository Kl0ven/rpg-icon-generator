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
    
    def __repr__(self):
        return str(self)

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length
        return self

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def length_Sq(self):
        return self.x * self.x + self.y * self.y

    def distance_to(self, x, y):
        return math.sqrt(self.distance_to_sq(x, y))

    def distance_to_sq(self, x, y=None):
        if y is None:
            dx = self.x - x.x
            dy = self.y - x.y
        else:
            dx = self.x - x
            dy = self.y - y
        return dx * dx + dy * dy

    def add_vector(self, v):
        self.x += v.x
        self.y += v.y
        return self

    def lerp_to(self, v, t):
        self.x = (v.x - self.x) * t + self.x
        self.y = (v.y - self.y) * t + self.y
        return self

    def multiply_scalar(self, v):
        self.x *= v
        self.y *= v
        return self

    def dot_product(self, x, y=None):
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

    def rotate(self, radians, origin=None):
        origin = origin if origin is not None else Vector(0, 0)
        x, y = self.x, self.y
        offset_x, offset_y = origin.x, origin.y
        adjusted_x = (x - offset_x)
        adjusted_y = (y - offset_y)
        cos_rad = math.cos(radians)
        sin_rad = math.sin(radians)
        self.x = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
        self.y = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y

        return self

    def round(self):
        self.x = round(self.x)
        self.y = round(self.y)
        return self
