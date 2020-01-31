import pygame
from entity import MazeRunner
from constants import *

class Fruit(MazeRunner):
    def __init__(self, nodes, spritesheet, level):
        MazeRunner.__init__(self, nodes, spritesheet)
        self.name = "fruit"
        self.color = (0,200,0)
        self.setStartPosition()
        self.lifespan = 5
        self.timer = 0
        self.killme = False
        self.points = 200
        self.setup()
        self.image = self.getImage(level)
        
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.lifespan:
            self.killme = True
            
    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node.neighbors[LEFT]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2

    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.fruitStart:
                return node
        return None

    def setup(self):
        self.fruits = {}
        self.fruits["cherry"] = self.spritesheet.getImage(8,2,32,32)
        self.fruits["banana"] = self.spritesheet.getImage(9,2,32,32)
        self.fruits["apple"] = self.spritesheet.getImage(10,2,32,32)
        self.fruits["strawberry"] = self.spritesheet.getImage(8,3,32,32)
        self.fruits["orange"] = self.spritesheet.getImage(9,3,32,32)
        self.fruits["watermelon"] = self.spritesheet.getImage(10,3,32,32)

    def getImage(self, level):
        if level < 1: self.name = "cherry"
        elif level < 2: self.name = "banana"
        elif level < 3: self.name = "apple"
        elif level < 20: self.name = "strawberry"
        elif level < 25: self.name = "orange"
        else: self.name = "watermelon"
        return self.fruits[self.name]

    def collect(self):
        return self.fruits[self.name]


class FruitTrophy(object):
    def __init__(self):
        self.names = []
        self.trophies = {}
        self.y = TILEHEIGHT * NROWS - 32
        
    def add(self, name, image):
        if name not in self.names:
            self.names.append(name)
            index = len(self.trophies)
            self.trophies[TILEWIDTH*NCOLS-32*(index+1)] = image
            #self.trophies.append(image)

    def render(self, screen):
        for xkey in self.trophies.keys():
            screen.blit(self.trophies[xkey], (xkey, self.y))
