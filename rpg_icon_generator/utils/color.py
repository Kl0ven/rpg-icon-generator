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

    def darken(self, t):
        self.r *= (1-t)
        self.g *= (1-t)
        self.b *= (1-t)
        return self

    def __str__(self):
        return "Color(R: {}, G: {}, B: {}, A: {})".format(self.r, self.g, self.b, self.a)

    def __repr__(self):
        return str(self)

    def lighten(self, t):
        t = 1-t
        self.r = (1 - (1 - self.r/255) * t) * 255
        self.g = (1 - (1 - self.g/255) * t) * 255
        self.b = (1 - (1 - self.b/255) * t) * 255
        return self 

    def randomize(self, maxamt, r):
        maxamtHalf = math.floor(maxamt/2)
        self.r = max(0, min(255, self.r + r.range(-maxamtHalf, maxamtHalf)))
        self.g = max(0, min(255, self.g + r.range(-maxamtHalf, maxamtHalf)))
        self.b = max(0, min(255, self.b + r.range(-maxamtHalf, maxamtHalf)))
        return self
    
    def copy(self):
        return copy.deepcopy(self)

    def to_hex(self):
        return '#{:02x}{:02x}{:02x}'.format(math.floor(self.r), math.floor(self.g), math.floor(self.b))

    def is_black(self):
        return self.a == 1 and self.r == 0 and self.g == 0 and self.b == 0

    def is_empty(self, ignore_black=False):
        return (self.a == 0 or self.is_black() if ignore_black else False)

    def get_tetradic(self):
        r, g, b = map(lambda x: x/255.0, [self.r, self.g, self.b])
        #hls provides color in radial scale
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        #get hue changes at 120 and 240 degrees
        deg_60_hue = h + (60.0 / 360.0)
        deg_180_hue = h + (180.0 / 360.0)
        deg_240_hue = h + (240.0 / 360.0)
        #convert to rgb
        color_60_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_60_hue, l, s)))
        color_180_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_180_hue, l, s)))
        color_240_rgb = list(map(lambda x: round(x * 255),colorsys.hls_to_rgb(deg_240_hue, l, s)))
        return [Color(*color_60_rgb), Color(*color_180_rgb), Color(*color_240_rgb)]

    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b and self.a == other.a

    @staticmethod
    def hsv2rgb(h, s, v):
        r, g, b = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h/360, s, v))
        return Color(r, g, b)

    @staticmethod
    def lerp(a, b, t):
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
        r = random.range(0, 256)
        g = random.range(0, 256)
        b = random.range(0, 256)
        return Color(r, g, b)
