import math
import bezier
from rpg_icon_generator.utils.vector import Vector
from rpg_icon_generator.generator.__generator import Generator
from rpg_icon_generator.utils.misc import float_range
from itertools import product
from rpg_icon_generator.utils.color import Color


class Armor_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension, complexity)

        armor_width = self.turtle_bound.w - self.random.randomRange(0, 6)
        armor_height = self.turtle_bound.h
        center = Vector((self.turtle_bound.w/2) + self.turtle_bound.x,
                        (self.turtle_bound.h/2) + self.turtle_bound.y)

        # the amount of symmetry for the armor
        armorSymmetry = 0 if self.random.randomFloat() < 0.2 else 1

        bottom_radius = Vector(self.random.randomRange(5, int(armor_width*0.3)), 
                            self.random.randomRange(5, int(armor_height*0.3)))
        corners = []
        for multx, multy in product([-1, 1], repeat=2):
            corners.append(center.copy().addVector(Vector(armor_width/2 * multx, armor_height/2 * multy)))

        ploy_point = [corners[0]]
        bottom_corner = corners[1]
        curve_point = self.curve(Vector(bottom_corner.x, bottom_corner.y - bottom_radius.y),
                                Vector(bottom_corner.x + bottom_radius.x, bottom_corner.y),
                                Vector(bottom_corner.x, bottom_corner.y))
        ploy_point += curve_point

        if armorSymmetry:
            for p in curve_point[::-1]:
                ploy_point.append(Vector(self.drawing_bound.w - p.x, p.y))
        else:
            bottom_corner = corners[3]
            ploy_point += self.curve(Vector(bottom_corner.x - bottom_radius.x, bottom_corner.y),
                                    Vector(bottom_corner.x, bottom_corner.y - bottom_radius.y),
                                    Vector(bottom_corner.x, bottom_corner.y))

        ploy_point.append(corners[2])

        for i, p in enumerate(ploy_point):
            c = Color.hsv2rgb(int((i/len(ploy_point))*360), 1, 1)
            self.draw_pixel(p.x, p.y, c)


        # self._draw_border()
        # self._draw_rarity_border(complexity)
        self.export(seed)


    def curve(self, vstart, vstop, vanchor):
        nodes = [
            [vstart.x, vanchor.x, vstop.x],
            [vstart.y, vanchor.y, vstop.y]
        ]
        curve = bezier.Curve(nodes, degree=2)
        points = []
        for s in float_range(0, 1, 0.1):
            pos = curve.evaluate(s)
            points.append(Vector(pos[0][0], pos[1][0]))
        return points
