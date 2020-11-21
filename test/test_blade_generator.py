import unittest
from rpg_icon_generator import Blade_Generator
from datetime import datetime
import os.path

class Test_blade_generation(unittest.TestCase):

    def test_generation(self):
        generator = Blade_Generator()
        seed = datetime.now()
        generator.generate(seed=seed, dimension=32, output_directory='./test/out/')
        self.assertTrue(os.path.isfile("./test/out/{}.png".format(seed)))

if __name__ == '__main__':
    unittest.main()
