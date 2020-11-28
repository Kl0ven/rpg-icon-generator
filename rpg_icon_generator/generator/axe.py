from rpg_icon_generator.utils.vector import Vector
import math

from rpg_icon_generator.generator.__generator import Generator


class Axe_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension, complexity)

        self._draw_axe_blade_helper(
            origine=Vector(self.drawing_bound.w/2, self.drawing_bound.h/2),
            offset=10
            )

        # self._draw_border()
        # self._draw_rarity_border(complexity)
        self.export(seed)
