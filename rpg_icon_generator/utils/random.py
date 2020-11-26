import random

class Random:
    def __init__(self, seed):
        random.seed(seed)

    def randomFloat(self):
        return random.random()

    def randomFloatLow(self):
        v = random.random()
        return v * v

    def randomRange(self, a, b):
        try:
            return random.randrange(a, b)
        except ValueError:
            return a
    def randomRangeFloat(self, a, b):
        return random.uniform(a, b)

    def randomFloatExtreme(self):
        rand = random.random()*2 - 1
        return rand * rand

    def randomFloatHigh(self):
        return 1-self.randomFloatLow()

    def randomRangeFloatHigh(self, min, max):
        return self.randomFloatHigh() * (max - min) + min
