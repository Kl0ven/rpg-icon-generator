from rpg_icon_generator.utils.vector import Vector
import math

from rpg_icon_generator.generator.__generator import Generator


class Blade_Generator(Generator):
    def generate(self, seed, dimension, render_scale, output_directory, complexity):
        self.reset_canvas(dimension, render_scale, output_directory)
        self.set_seed(seed)
        self.set_drawing_bound(dimension)
        

        # length of the pommel
        pommelLength = math.ceil(self.random.randomFloatLow() * 2 * self.dscale)
        # length of the hilt
        hiltLength = math.ceil(self.random.randomRange(6, 11) * self.dscale)
        # width of the xguard
        xguardWidth = math.ceil(self.random.randomRange(1, 4) * self.dscale)

        bladeResults = self._draw_blade_helper(pommelLength + hiltLength + xguardWidth)

        # draw the hilt
        hiltStartDiag = math.floor((pommelLength * math.sqrt(2)))
        hiltParams = {
            "startDiag": hiltStartDiag,
            "lengthDiag": math.floor(bladeResults["startOrtho"] - hiltStartDiag),
            "maxRadius": bladeResults["startRadius"]
        }
        self._draw_grip_helper(hiltParams)

        # draw the crossguard
        crossguardParams = {
            "positionDiag": bladeResults["startOrtho"],
            "halfLength": bladeResults["startRadius"] * (1 + 2 * self.random.randomFloatLow()) + 1
        }
        crossguardResults = self._draw_crossguard_helper(crossguardParams)

        # draw the pommel
        pommelRadius = pommelLength * math.sqrt(2) / 2
        pommelParams = {
            "center": Vector(math.floor(pommelRadius + 1) + self.turtle_bound.x*2, math.ceil(self.turtle_bound.h - pommelRadius - 1)),
            "radius": pommelRadius,
            "colorLight": crossguardResults["colorLight"],
            "colorDark": crossguardResults["colorDark"]
        }
        self._draw_round_ornament_helper(pommelParams)

        self._draw_border()
        self._draw_rarity_border(complexity)
        for x in range(self.turtle_bound.x, self.turtle_bound.w + self.turtle_bound.x):
            for y in range(self.turtle_bound.y, self.turtle_bound.h + self.turtle_bound.y):
                self.draw_red_pixel(x, y)
        self.export(seed)
