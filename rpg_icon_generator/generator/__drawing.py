import drawSvg as draw
from rpg_icon_generator.utils.color import Color
import math
import os

class Drawing(object):
    def reset_canvas(self, dimension, render_scale, output_directory):
        self.draw = draw.Drawing(dimension, dimension, origine=(0, dimension))
        self.dimension = dimension
        self.out_dir = output_directory
        self.image = [[None]* dimension for _ in range(dimension)]
        self.render_scale = render_scale
    
    def rasterize(self):
        return self.draw.rasterize()

    def export(self, name):
        path = os.path.join(self.out_dir, "{}.png".format(name))
        self.draw.setPixelScale(self.render_scale)
        self.draw.savePng(path)

    def draw_pixel(self, x, y, c):
        self.image[x][y] = c
        r = draw.Rectangle(x, -y + self.dimension - 1, 1, 1, fill=c.to_hex(), fill_opacity=c.a)
        self.draw.append(r)

    # debug only
    def draw_red_pixel(self, x, y, a=0.2):
        r = draw.Rectangle(x, -y + self.dimension - 1, 1, 1, fill="red", fill_opacity=a)
        self.draw.append(r)

    def get_pixel_data(self, x, y):
        if x < 0 or x >= self.dimension or y < 0 or y >= self.dimension:
            return None
        c = self.image[x][y]
        return c if c is not None else Color(0,0,0,0)
