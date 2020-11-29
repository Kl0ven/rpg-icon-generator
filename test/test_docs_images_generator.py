import unittest
from rpg_icon_generator import Potion_Generator, Axe_Generator, Blade_Generator
from rpg_icon_generator.utils.constants import RARITY_RANGE
from datetime import datetime
import os.path
import random

class Test_docs_images_generation(unittest.TestCase):

    def test_docs_images_blade(self):
        generator = Blade_Generator()
        for name, c in RARITY_RANGE.items():
            seed = "blade_{}".format(c[0])
            generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=c[0])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
            seed = "blade_{}".format(c[1])
            generator.generate(seed=seed, dimension=64, render_scale=2,output_directory='./test/out/', complexity=c[1])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))

    def test_docs_images_potion(self):
        generator = Potion_Generator()
        for name, c in RARITY_RANGE.items():
            seed = "potion_{}".format(c[0])
            generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=c[0])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
            seed = "potion_{}".format(c[1])
            generator.generate(seed=seed, dimension=64, render_scale=2,output_directory='./test/out/', complexity=c[1])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))

    def test_docs_images_axe(self):
        generator = Axe_Generator()
        for name, c in RARITY_RANGE.items():
            seed = "axe_{}".format(c[0])
            generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=c[0])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
            seed = "axe_{}".format(c[1])
            generator.generate(seed=seed, dimension=64, render_scale=2,output_directory='./test/out/', complexity=c[1])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
if __name__ == '__main__':
    unittest.main()
