import drawSvg as draw
import math
import os

class Drawing(object):
    def reset_canvas(self, dimension, output_directory):
        self.draw = draw.Drawing(dimension, dimension, origine=(0, dimension))
        self.dimension = dimension
        self.out_dir = output_directory

    def get_color_string(self, c):
        if c.get("a"):
            return '#{:02x}{:02x}{:02x}'.format(math.floor(c["r"]), math.floor(c["g"]), math.floor(c["b"]))
        else:
            return '#{:02x}{:02x}{:02x}{:02x}'.format(math.floor(c["r"]), math.floor(c["g"]), math.floor(c["b"]), math.floor(c["a"] * 255))
    
    def export(self, name):
        path = os.path.join(self.out_dir, "{}.png".format(name))
        self.draw.savePng(path)

    def draw_pixel(self, x, y, c):
        r = draw.Rectangle(x, -y + self.dimension, 1, 1, fill=self.get_color_string(c))
        self.draw.append(r)
