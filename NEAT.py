global edgeDict
edgeDict = []

class Organism():
    def __init__(self, numInputNodes, numOutputNodes):
        self.numInputNodes = numInputNodes
        self.numOutputNodes = numOutputNodes
        self.nodes = [i for i in range(0, numInputNodes + numOutputNodes)]
        self.edges = {}
        self.fitness = -1

    def add_edge(self, sequence, weight):
        return 0

    def disable_edge(self, iD):
        return 0

    def add_node(self, iD, sequence, weightPrev, weightNext):
        return 0

    def forward_prop(self, inputNodes):
        return 0

class Selection():
    def crossbreed(organism1, organism2):
        return 0

    def selection(oldGen, population):
        return 0

class Mutation():
    def mutate_enable_disable(org):
        return 0


    def mutate_weight_shift(org):
        return 0

    def mutate_weight_random(org):
        return 0

    def mutate_link(org):
        return 0

    def mutate_node(org):
        return 0

    def mutate(newGen, percentage):
        return 0


