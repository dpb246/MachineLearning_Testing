import random
from copy import deepcopy
'''
Stores all the accel vectors
'''
class brain:
    def __init__(self, number_of_steps, mutation_rate = 0.01):
        self.mutation_rate = mutation_rate
        self.steps = []
        self.number_of_steps = number_of_steps
        self.counter = 0
        self.done = False
        self.randomize()
    def randomize(self):
        self.steps = [[random.random()*random.randrange(-1, 2, 2)/4 for i in range(2)] for i in range(self.number_of_steps)] #Random steps
    def add_more(self, number_to_add):
        for i in number_to_add:
            self.steps.append([random.random()*random.randrange(-1, 2, 2)/4 for i in range(2)])
    def get_next(self):
        if self.done: return None
        self.counter += 1
        if not self.counter < self.number_of_steps:
            self.done = True
            return None
        return self.steps[self.counter]
    def reset(self):
        self.done = False
        self.counter = 0
    def mutate(self):
        for index, element in enumerate(self.steps):
            if random.random() < self.mutation_rate:
                #self.steps[index] = [random.random()*random.randrange(-1, 2, 2)/4 for i in range(2)]
                for i in range(2):
                    self.steps[index][i] += (random.random()*random.randrange(-1, 2, 2)/4) / 10 #Step 1/100 in a direction
        if random.random() < 0.05:
            self.mutation_rate += (random.random()*random.randrange(-1, 2, 2)/4) / 100
    def special_mutate(self, steps_taken):
        for index, element in enumerate(self.steps[-(self.number_of_steps-steps_taken+100):]):#only mutate last few
            if random.random() < self.mutation_rate:
                for i in range(2):
                    self.steps[index][i] += (random.random()*random.randrange(-1, 2, 2)/4) / 10
        if random.random() < 0.05:
            self.mutation_rate += (random.random()*random.randrange(-1, 2, 2)/4) / 100
