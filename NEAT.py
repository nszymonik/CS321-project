import math, random

global edgeDict
edgeDict = []

def sequence_to_id(sequence):
    if sequence in edgeDict:
        return edgeDict.index(sequence)
    return -1

def sigmoid(x):
	if x > 300:
		return 1
	elif x < -300:
		return 0
	return (1/(1 + round(math.pow(math.e, -x), 5)))

class Organism():
    def __init__(self, numInputNodes, numOutputNodes):
        self.numInputNodes = numInputNodes
        self.numOutputNodes = numOutputNodes
        self.nodes = [i for i in range(0, numInputNodes + numOutputNodes)]
        self.edges = {}
        self.fitness = -1

    def isOutput(self, n):
        return (n >= self.numInputNodes and n < self.numOutputNodes)

    def isInput(self, n):
        return (n < self.numInputNodes)

    def add_edge(self, n1, n2, weight):
        sequence = (n1, n2)
        if not isOutput(n2) and n1 > n2:
            sequence = (n2, n1)
        if sequence not in edgeDict:
            edgeDict.add(sequence)
        iD = edgeDict.index(sequence)
        self.edges[iD] = (weight, 1)

    def disable_edge(self, iD):
        self.edges[iD][1] = 0 

    def add_node(self, iD, weightPrev, weightNext):
        s = edgeDict[iD]
        del self.edges[iD]
        self.add_edge(self, s[0], len(self.nodes), weightPrev)
        self.add_edge(self, len(self.nodes), s[1], weightNext)
        self.nodes.append(len(self.nodes))

    def recurse_node(self, n, inputVals):
        inp = []
        ret = 0
        
        for key in self.edges:
            if edgeDict[key][1] == n:
                inp.append(key)

        for i in inp:
            if isInput(edgeDict[i][0]):
                ret += inputVals[edgeDict[i][0]]*self.edges[i][0]*self.edges[i][1]
            else:
                ret += recurse_node(self, edgeDict[i][0], inputVals)*self.edges[i][0]*self.edges[i][1]

        return sigmoid(ret)

    def forward_prop(self, inputVals):
        outputVals = []

        for i in range(0, self.numOutputNodes):
            outputVals.append(recurse_node(self, self.numInputNodes + i, inputVals))

        return outputVals

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


