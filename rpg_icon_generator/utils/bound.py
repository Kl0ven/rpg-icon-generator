class Bound:
    def __init__(self, x, y, w, h):
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        if y is None:
            if x is not None:
                self.x = x.x
                self.y = x.y
                self.w = x.w
                self.h = x.h
        else:
            self.x = x
            self.y = y
            self.w = w
            self.h = h

    def contains(self, v):
        x = v.x
        y = v.y
        return x >= self.x and y >= self.y and x < self.x + self.w and y < self.y + self.h
