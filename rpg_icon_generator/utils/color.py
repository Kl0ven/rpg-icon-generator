import math
import random 
import colorsys
import copy

class Color:
    def __init__(self, r, g, b, a=1):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def colorDarken(self, t):
        self.r *= (1-t)
        self.g *= (1-t)
        self.b *= (1-t)
        return self

    def colorLighten(self, t):
        t = 1-t
        self.r = (1 - (1 - self.r/255) * t) * 255
        self.g = (1 - (1 - self.g/255) * t) * 255
        self.b = (1 - (1 - self.b/255) * t) * 255
        return self 

    def colorRandomize(self, maxamt, r):
        maxamtHalf = math.floor(maxamt/2)
        self.r = max(0, min(255, self.r + r.randomRange(-maxamtHalf, maxamtHalf)))
        self.g = max(0, min(255, self.g + r.randomRange(-maxamtHalf, maxamtHalf)))
        self.b = max(0, min(255, self.b + r.randomRange(-maxamtHalf, maxamtHalf)))
        return self
    
    def copy(self):
        return copy.deepcopy(self)

    def to_hex(self):
        return '#{:02x}{:02x}{:02x}'.format(math.floor(self.r), math.floor(self.g), math.floor(self.b))

    @staticmethod
    def hsv2rgb(h, s, v):
        r, g, b = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/360, s, v))
        return Color(r, g, b)

    @staticmethod
    def colorLerp(a, b, t):
        t = max(0, min(1, t))
        cr = (b.r - a.r) * t + a.r
        cg = (b.g - a.g) * t + a.g
        cb = (b.b - a.b) * t + a.b
        aa = a.a
        ba = b.a
        ca = (ba - aa) * t + aa
        return Color(cr, cg, cb, ca)

    @staticmethod
    def random_color(random):
        r = random.randomRange(0, 256)
        g = random.randomRange(0, 256)
        b = random.randomRange(0, 256)
        return Color(r, g, b)
