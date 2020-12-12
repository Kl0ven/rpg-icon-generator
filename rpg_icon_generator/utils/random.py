import random

class Random:
    def __init__(self, seed):
        random.seed(seed)

    def float(self):
        return random.random()

    def float_low(self):
        v = random.random()
        return v * v

    def range(self, a, b):
        try:
            return random.randrange(a, b)
        except ValueError:
            return a
    def range_float(self, a, b):
        return random.uniform(a, b)

    def float_extreme(self):
        rand = random.random()*2 - 1
        return rand * rand

    def float_high(self):
        return 1-self.float_low()

    def range_float_high(self, min, max):
        return self.float_high() * (max - min) + min

    def choice(self, arr):
        return random.choice(arr)
