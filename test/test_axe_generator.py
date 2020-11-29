import unittest
from rpg_icon_generator import Axe_Generator
from rpg_icon_generator.utils.constants import RARITY_RANGE
from datetime import datetime
import os.path
import random

class Test_axe_generation(unittest.TestCase):

    def test_generation(self):
        generator = Axe_Generator()
        seed = datetime.now()
        seed = "2020-11-28 20:44:43.6896078"
        generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=50)
        self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))

    def test_generation_chain(self):
        generator = Axe_Generator()
        for i in range(10):
            seed = str(datetime.now()) + str(i)
            generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=random.randrange(0, 101))
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))

    def test_generation_all_complexity(self):
        generator = Axe_Generator()
        for name, c in RARITY_RANGE.items():
            date = str(datetime.now())
            seed = "{}_min_{}".format(date, name)
            generator.generate(seed=seed, dimension=64, render_scale=2, output_directory='./test/out/', complexity=c[0])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
            seed = "{}_max_{}".format(date, name)
            generator.generate(seed=seed, dimension=64, render_scale=2,output_directory='./test/out/', complexity=c[1])
            self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))
        

if __name__ == '__main__':
    unittest.main()
