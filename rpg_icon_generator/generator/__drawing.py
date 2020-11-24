import drawSvg as draw
import math
import os
import numpy

class Drawing(object):
    def reset_canvas(self, dimension, render_scale, output_directory):
        self.draw = draw.Drawing(dimension, dimension, origine=(0, dimension))
        self.dimension = dimension
        self.out_dir = output_directory
        self.image = numpy.zeros(shape=(dimension, dimension, 4))
        self.render_scale = render_scale
    
    def rasterize(self):
        return self.draw.rasterize()

    def get_color_string(self, c):
        if c.get("a"):
            return '#{:02x}{:02x}{:02x}'.format(math.floor(c["r"]), math.floor(c["g"]), math.floor(c["b"]))
        else:
            return '#{:02x}{:02x}{:02x}{:02x}'.format(math.floor(c["r"]), math.floor(c["g"]), math.floor(c["b"]), math.floor(c["a"] * 255))
    
    def export(self, name):
        path = os.path.join(self.out_dir, "{}.png".format(name))
        self.draw.setPixelScale(self.render_scale)
        self.draw.savePng(path)

    def draw_pixel(self, x, y, c):
        self.image[x][y][0] = c["r"]
        self.image[x][y][1] = c["g"]
        self.image[x][y][2] = c["b"]
        self.image[x][y][3] = c["a"]
        r = draw.Rectangle(x, -y + self.dimension - 1, 1, 1, fill=self.get_color_string(c), fill_opacity=c["a"])
        self.draw.append(r)

    # debug only
    def draw_red_pixel(self, x, y, a=0.2):
        r = draw.Rectangle(x, -y + self.dimension - 1, 1, 1, fill="red", fill_opacity=a)
        self.draw.append(r)

    def get_pixel_data(self, x, y):
        if x < 0 or x >= self.dimension or y < 0 or y >= self.dimension:
            return None
        return self.image[x][y]
