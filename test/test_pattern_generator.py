import unittest
from rpg_icon_generator.generator.__pattern_generator import Pattern_Generator
from rpg_icon_generator.utils.random import Random
from datetime import datetime

class Test_pattern_generation(unittest.TestCase):

    def test_generation(self):
        seed = datetime.now()
        r = Random(seed)
        p = Pattern_Generator(30, r)
        for _ in range(30):
            p.print()
            p.step()

if __name__ == '__main__':
    unittest.main()
