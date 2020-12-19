from rpg_icon_generator.utils.vector import Vector
import math

from rpg_icon_generator.generator.__generator import Generator


class Hammer_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension, complexity)

        # length of the pommel
        pommelLength = math.ceil(self.random.float_low() * 2 * self.dscale)

        hiltStartDiag = math.floor((pommelLength * math.sqrt(2)))

        # length of the hilt
        lengthDiag = (self.turtle_bound.w - hiltStartDiag) * 0.8

        # draw the hilt
        hiltParams = {
            "startDiag": hiltStartDiag,
            "lengthDiag": lengthDiag,
            "maxRadius": None
        }
        grip_size = self._draw_grip_helper(hiltParams)

        complexity_factor = (complexity/100) + 0.5
        body_width = (self.random.range(8, 20) + grip_size) * complexity_factor
        body_heigth = self.random.range(8, 15) * complexity_factor
        dark_color, light_color = self._draw_hammer_helper(
            origine=Vector(
                (self.turtle_bound.x + lengthDiag) - 2, 
                self.drawing_bound.h - ((self.turtle_bound.y + lengthDiag) - 2)),
            body_width=body_width,
            body_heigth=body_heigth
            )

        # draw the pommel
        pommelRadius = pommelLength * math.sqrt(2) / 2
        pommelParams = {
            "center": Vector(math.floor(pommelRadius + self.turtle_bound.x), math.ceil(self.drawing_bound.h - (pommelRadius + self.turtle_bound.y))),
            "radius": pommelRadius,
            "colorLight": light_color,
            "colorDark": dark_color
        }
        self._draw_round_ornament_helper(pommelParams)


        self._draw_border()
        self._draw_rarity_border(complexity)
        self.export(seed)
