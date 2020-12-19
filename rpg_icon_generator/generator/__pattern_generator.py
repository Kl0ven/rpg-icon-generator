import itertools

class Node(object):
    def __init__(self, value):
        self.value = value
        self.other = None
    
    def set_links(self, other):
        self.other = other

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return "Node: {}".format(self.value)

    
class Pattern_Generator(object):
    def __init__(self, h, r, nb_links=3):
        self.height = h
        self.r = r
        self.nodes = []
        self.nb_links = nb_links
        self.truth_table = {}
        for _ in range(h):
            self.nodes.append(Node(r.bool()))

        for n in self.nodes:
            n.set_links(r.choice(self.nodes, nb_links))

        for p in itertools.product(("1", "0"), repeat=nb_links):
            p_str = "".join(p)
            self.truth_table[p_str] = r.bool()

    def step(self):
        for n in self.nodes:
            p_str = "".join(["1" if o.value else "0" for o in n.other])  
            n.value = self.truth_table[p_str]

    def print(self):
        print("".join(["█" if n.value else " " for n in self.nodes]))
