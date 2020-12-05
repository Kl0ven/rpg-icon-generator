import math
import bezier
from itertools import product
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from rpg_icon_generator.utils.vector import Vector
from rpg_icon_generator.generator.__generator import Generator
from rpg_icon_generator.utils.misc import float_range
from rpg_icon_generator.utils.color import Color


class Armor_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension, complexity)

        lower = int(self.turtle_bound.w*0.15)
        upper = int(self.turtle_bound.w*0.2)
        shoulder_width = max(4, self.random.randomRange(lower, upper))
        shoulder_height = max(4, self.random.randomRange(lower, upper))
        armor_width = max(10, self.turtle_bound.w - self.random.randomRange(0, 6) - (2 * shoulder_width))
        armor_height = max(15 + shoulder_height, self.turtle_bound.h)
        center = Vector((self.turtle_bound.w/2) + self.turtle_bound.x,
                        (self.turtle_bound.h/2) + self.turtle_bound.y)
        armor_color = Color.hsv2rgb(
            self.random.randomRangeFloat(0, 360),
            self.random.randomFloatExtreme() * 0.6 if self.random.randomFloat() < 0.3 else 0,
            self.random.randomRangeFloat(0.75, 1)
        )

        # the amount of symmetry for the armor
        armorSymmetry = 0 if self.random.randomFloat() < 0.2 else 1

        bottom_radius = Vector(self.random.randomRange(5, int(armor_width*0.3)), 
                            self.random.randomRange(5, int(armor_height*0.3)))
        corners = []
        for multx, multy in product([-1, 1], repeat=2):
            corners.append(center.copy().addVector(Vector(armor_width/2 * multx, armor_height/2 * multy)))

        poly_points = [corners[0]]

        # left shoulder
        poly_points.append(corners[0].copy().addVector(Vector(-shoulder_width, 0)))
        poly_points.append(corners[0].copy().addVector(Vector(-shoulder_width, shoulder_height)))
        poly_points.append(corners[0].copy().addVector(Vector(0, shoulder_height)))

        # bottom left curve
        bottom_corner = corners[1]
        curve_point = self.curve(Vector(bottom_corner.x, bottom_corner.y - bottom_radius.y),
                                Vector(bottom_corner.x + bottom_radius.x, bottom_corner.y),
                                Vector(bottom_corner.x, bottom_corner.y))
        poly_points += curve_point

        # bottom right curve
        if armorSymmetry:
            for p in curve_point[::-1]:
                poly_points.append(Vector(self.drawing_bound.w - p.x, p.y))
        else:
            bottom_corner = corners[3]
            poly_points += self.curve(Vector(bottom_corner.x - bottom_radius.x, bottom_corner.y),
                                    Vector(bottom_corner.x, bottom_corner.y - bottom_radius.y),
                                    Vector(bottom_corner.x, bottom_corner.y))
        
        # right shoulder
        poly_points.append(corners[2].copy().addVector(Vector(0, shoulder_height)))
        poly_points.append(corners[2].copy().addVector(Vector(shoulder_width, shoulder_height)))
        poly_points.append(corners[2].copy().addVector(Vector(shoulder_width, 0)))

        poly_points.append(corners[2])

        poly = Polygon([p.to_coord() for p in poly_points])
        for x in range(self.drawing_bound.w):
            for y in range(self.drawing_bound.h):
                pt = Point(x, y)
                if poly.contains(pt):
                    self.draw_pixel(x, y, armor_color)

        # for i, p in enumerate(poly_points):
        #     c = Color.hsv2rgb(int((i/len(poly_points))*360), 1, 1)
        #     self.draw_pixel(p.x, p.y, c)

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
