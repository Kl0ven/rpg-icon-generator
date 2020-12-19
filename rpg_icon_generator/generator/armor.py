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
        shoulder_width = max(4, self.random.range(lower, upper))
        shoulder_height = max(4, self.random.range(lower, upper))
        armor_width = max(10, self.turtle_bound.w - self.random.range(0, 6) - (2 * shoulder_width))
        if armor_width % 2 != 0:
            armor_width += 1
        armor_height = max(15 + shoulder_height, int(self.turtle_bound.h * 0.9))
        center = Vector((self.turtle_bound.w/2) + self.turtle_bound.x,
                        (self.turtle_bound.h/2) + self.turtle_bound.y)
        armor_color = Color.hsv2rgb(
            self.random.range_float(0, 360),
            self.random.range_float(0.3, 1) * 1 if self.random.float() < 0.9 else 0.1,
            self.random.range_float(0.75, 1)
        )
        armor_secodary_color = self.random.choice(armor_color.get_tetradic())
        neck_width = max(5, self.random.range(int(armor_width*0.25), int(armor_width*0.5)))
        neck_depth = self.random.range(5, 10)
        cape_height = self.random.range(int(armor_height*0.1), int(armor_height*0.3))

        # the amount of symmetry for the armor
        armorSymmetry = 0 if self.random.float() < 0.2 else 1

        bottom_radius = Vector(self.random.range(5, int(armor_width*0.3)), 
                            self.random.range(5, int(armor_height*0.3)))
        corners = []
        for multx, multy in product([-1, 1], repeat=2):
            corners.append(center.copy().add_vector(Vector(armor_width/2 * multx, armor_height/2 * multy)))

        anchores = self._draw_armor(corners, shoulder_width, shoulder_height, bottom_radius,
                        armorSymmetry, center, neck_depth, neck_width, armor_color)

        self._draw_shoulder_accent(corners, anchores, cape_height, shoulder_width, shoulder_height, armor_secodary_color)

        self._draw_inprint(anchores[-1], center)

        self._draw_border()
        self._draw_rarity_border(complexity)
        self.export(seed)

    def _draw_inprint(self, bottom_anchor, center, dark_amount=0.1, min_height=5):
        width = 0
        height = 0
        for x in range(self.drawing_bound.w):
            pixel = self.get_pixel_data(x, bottom_anchor.y)
            if not pixel.is_empty(ignore_black=True):
                self.draw_pixel(x, bottom_anchor.y, pixel.copy().darken(dark_amount))
                width += 1

        for y in range(0, int(bottom_anchor.y)):
            pixel = self.get_pixel_data(center.x, y)
            if not pixel.is_empty(ignore_black=True):
                self.draw_pixel(center.x, y, pixel.copy().darken(dark_amount))
                height += 1

        height_6_packs = height - int(height*0.5)
        y = int(bottom_anchor.y) - min_height
        packs_width = width*0.8
        while y > (bottom_anchor.y - height_6_packs):
            for dx in range(1, int(packs_width/2)):
                # Right
                pixel = self.get_pixel_data(center.x + dx, y)
                if not pixel.is_empty(ignore_black=True):
                    self.draw_pixel(center.x + dx, y, pixel.copy().darken(dark_amount))
                # Left
                pixel = self.get_pixel_data(center.x - dx, y)
                if not pixel.is_empty(ignore_black=True):
                    self.draw_pixel(center.x - dx, y, pixel.copy().darken(dark_amount))
            packs_width *= 0.8
            y -= min_height


    def _draw_shoulder_accent(self, corners, anchores, cape_height, shoulder_width, shoulder_height, armor_secodary_color):
        # left 
        poly_points = [anchores[0]]
        poly_points.append(corners[0].copy().add_vector(Vector(-shoulder_width, 0)))
        poly_points.append(corners[0].copy().add_vector(Vector(-shoulder_width, shoulder_height)))
        self._draw_poly(poly_points, armor_secodary_color)

        poly_points = []
        poly_points.append(corners[0].copy().add_vector(Vector(-shoulder_width+1, shoulder_height)))
        poly_points.append(anchores[2])
        poly_points.append(anchores[2].copy().add_vector(Vector(0, cape_height)))
        self._draw_poly(poly_points, armor_secodary_color, overwrite=False)

        # right
        poly_points = [anchores[1]]
        poly_points.append(corners[2].copy().add_vector(Vector(shoulder_width, 0)))
        poly_points.append(corners[2].copy().add_vector(Vector(shoulder_width, shoulder_height)))
        self._draw_poly(poly_points, armor_secodary_color)

        poly_points = []
        poly_points.append(corners[2].copy().add_vector(Vector(shoulder_width-1, shoulder_height)))
        poly_points.append(anchores[3])
        poly_points.append(anchores[3].copy().add_vector(Vector(0, cape_height)))
        self._draw_poly(poly_points, armor_secodary_color, overwrite=False)



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

    def _draw_armor(self, corners, shoulder_width, shoulder_height, bottom_radius, armorSymmetry, center, neck_depth, neck_width, armor_color):
        poly_points = [corners[0]]

        armpit_left = corners[0].copy().add_vector(Vector(0, shoulder_height))
        armpit_right = corners[2].copy().add_vector(Vector(0, shoulder_height))

        # left shoulder
        poly_points.append(corners[0].copy().add_vector(Vector(-shoulder_width, 0)))
        poly_points.append(corners[0].copy().add_vector(Vector(-shoulder_width, shoulder_height)))
        poly_points.append(armpit_left)

        # bottom left curve
        bottom_corner = corners[1]
        bottom_curve_start = Vector(bottom_corner.x, bottom_corner.y - bottom_radius.y)
        curve_point = self.curve(bottom_curve_start,
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
        poly_points.append(armpit_right)
        poly_points.append(corners[2].copy().add_vector(Vector(shoulder_width, shoulder_height)))
        poly_points.append(corners[2].copy().add_vector(Vector(shoulder_width, 0)))
        poly_points.append(corners[2])

        # neck
        center_neck = Vector(center.x, corners[2].y + neck_depth)
        left_anchor = center_neck.copy().add_vector(Vector(-neck_width/2, -neck_depth))
        right_anchor = center_neck.copy().add_vector(Vector(neck_width/2, -neck_depth))
        poly_points += self.curve(right_anchor, left_anchor, center_neck)

        poly_points.append(left_anchor)


        self._draw_poly(poly_points, armor_color)

        # harmpit edge case 
        self.draw_pixel(armpit_left.x, armpit_left.y, armor_color)
        self.draw_pixel(armpit_right.x, armpit_right.y, armor_color)

        # for i, p in enumerate(poly_points):
        #     c = Color.hsv2rgb(int((i/len(poly_points))*360), 1, 1)
        #     self.draw_pixel(p.x, p.y, c)

        self._draw_border()
        return [left_anchor, right_anchor, armpit_left, armpit_right, bottom_curve_start]

