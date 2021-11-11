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
        self.numNodes = numInputNodes + numOutputNodes
        #self.nodes = [i for i in range(0, numInputNodes + numOutputNodes)]
        self.edges = {}
        self.fitness = -1

    def is_output(self, n):
        return (n >= self.numInputNodes and n < self.numInputNodes + self.numOutputNodes)

    def is_input(self, n):
        return (n < self.numInputNodes)

    def contains_node(self, n):
        return (n < self.numNodes)
    
    def add_edge(self, n1, n2, weight):
        '''
        sequence = (n1, n2)
        if (self.is_output(n1)) or ((n1 > n2) and (not self.is_output(n2))):
            sequence = (n2, n1)
        '''
        sequence = {n1, n2}
        if sequence not in edgeDict:
            edgeDict.append(sequence)
        iD = edgeDict.index(sequence)
        self.edges[iD] = (weight, 1)

    def disable_edge(self, iD):
        self.edges[iD][1] = 0 

    def add_node(self, iD, weightPrev, weightNext):
        s = edgeDict[iD].copy()
        print(s)
        del self.edges[iD]
        self.add_edge(s.pop(), self.numNodes, weightPrev)
        self.add_edge(self.numNodes, s.pop(), weightNext)
        print(self.edges)
        print(edgeDict)
        self.numNodes += 1

    def copy_org(self):
        cOrg = Organism(self.numInputNodes, self.numOutputNodes)
        cOrg.numNodes = self.numNodes
        cOrg.fitness = self.fitness

        temp = {}
        for key in self.edges:
            temp[key] = self.edges[key][:]
        cOrg.edges = temp

        return cOrg

    def recurse_node(self, n, inputVals, visited):
        inp = []
        ret = 0

        visited.add(n)

        #print(n)
        for key in self.edges:
            if n in edgeDict[key]:
                #print(edgeDict[key])
                inp.append(key)

        for i in inp:
            node = (edgeDict[i] - {n}).pop()
            if self.is_input(node):
                ret += inputVals[node]*self.edges[i][0]*self.edges[i][1]
            elif node not in visited:
                ret += self.recurse_node(node, inputVals, visited)*self.edges[i][0]*self.edges[i][1]

        return sigmoid(ret)

    def forward_prop(self, inputVals):
        outputVals = []

        for i in range(0, self.numOutputNodes):
            outputVals.append(self.recurse_node(self.numInputNodes + i, inputVals, set()))

        return outputVals

class Selection():
    def crossbreed(self, org1, org2):
        otherOrg = org1.copy_org()
        newOrg = org2.copy_org()
        if org1.fitness > org2.fitness:
            temp = newOrg
            newOrg = otherOrg
            otherOrg = temp
        
        for key in otherOrg.edges:
            s = edgeDict[key].copy()
            if otherOrg.edges[key][1] and key not in newOrg.edges and newOrg.contains_node(s.pop()) and newOrg.contains_node(s.pop()):
                s = edgeDict[key].copy()
                newOrg.add_edge(s.pop(), s.pop(), otherOrg.edges[key][0])
        
        return newOrg

    def selection(self, oldGen, population):
        newGen = []

        oldGen.sort(key=lambda x: x.fitness, reverse=True)
        oldGen = oldGen[0:len(oldGen)//2]
        newGen.append(oldGen[0])

        for i in range(0, int(population/2 + 0.5) - 1):
            newGen.append(oldGen[random.randint(0,len(oldGen) - 1)])

        for i in range(int(population/2 + 0.5) - 1, population):
            newGen.append(self.crossbreed(oldGen[random.randint(0,len(oldGen) - 1)], oldGen[random.randint(0,len(oldGen) - 1)]))
        
        return newGen

class Mutation():
    def mutate_enable_disable(self, org):
        e = list(org.edges.keys())
        iD = e[random.randint(0, len(e) - 1)]
        org.edges[iD] = (org.edges[iD][0], 1 - org.edges[iD][1])

    def mutate_weight_shift(self, org):
        e = list(org.edges.keys())
        iD = e[random.randint(0, len(e) - 1)]
        org.edges[iD] = (org.edges[iD][0]*random.uniform(0, 2), 1)
        
    def mutate_weight_random(self, org):
        e = list(org.edges.keys())
        iD = e[random.randint(0, len(e) - 1)]
        org.edges[iD] = (random.uniform(-2, 2), org.edges[iD][1])

    def mutate_link(self, org):
        n1 = random.randint(0, org.numNodes - 1)
        n2 = random.randint(0, org.numNodes - 1)
        if org.is_input(n1):
            while org.is_input(n2):
                n2 = random.randint(0, org.numNodes - 1)
        elif org.is_output(n1):
            while org.is_output(n2):
                n2 = random.randint(0, org.numNodes - 1)

        org.add_edge(n1, n2, random.uniform(-2, 2))

    def mutate_node(self, org):
        e = list(org.edges.keys())
        iD = e[random.randint(0, len(e) - 1)]
        org.add_node(iD, org.edges[iD][0], random.uniform(-2, 2))
        
    def mutate_gen(self, gen, percentage):
        numMutes = int(len(gen)*percentage)
        for i in range(0, numMutes):
            muteOrg = gen[random.randint(0, numMutes - 1)]
            if len(muteOrg.edges) == 0:
                self.mutate_link(muteOrg)
            else:
                muteType = random.randint(0, 4)
                if muteType == 0:
                    self.mutate_enable_disable(muteOrg)
                elif muteType == 1:
                    self.mutate_weight_shift(muteOrg)
                elif muteType == 2:
                    self.mutate_weight_random(muteOrg)
                elif muteType == 3:
                    self.mutate_link(muteOrg)
                else:
                    self.mutate_node(muteOrg)
            
    
'''
a = Organism(3, 3)
a.add_edge(0, 3, 0.5)
a.add_edge(1, 3, 0.5)
a.add_edge(2, 3, 0.5)

a.add_edge(0, 4, 0.5)
a.add_edge(1, 4, 0.5)
a.add_edge(2, 4, 0.5)

a.add_edge(1, 5, 0.5)
a.add_edge(2, 5, 0.5)


a.add_node(1, 0.5, 0.5)
a.add_node(2, 0.5, 0.5)
a.add_node(3, 0.5, 0.5)

a.add_edge(6, 5, 0.75)
a.add_edge(7, 5, 0.5)
a.add_edge(8, 5, 0.75)

print(a.forward_prop(tuple((1, 1, 1))))

b = a.copy_org()
b.add_edge(6, 4, .88)

print(a.forward_prop(tuple((1, 1, 1))))
print(b.forward_prop(tuple((1, 1, 1))))

a.fitness = 500
gen = [a.copy_org(), b.copy_org(), a.copy_org(), b.copy_org(), b.copy_org(), b.copy_org(), a.copy_org(), a.copy_org()]
selector = Selection()
selector.selection(gen, len(gen))

mutator = Mutation()
mutator.mutate_gen(gen, 0.5)

for i in range(0, len(gen)):
    print(gen[i].edges)

for i in range(0, len(gen)):
    print(gen[i].forward_prop(tuple((1, 1, 1))))
'''
