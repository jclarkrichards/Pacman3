import pygame
from entity import MazeRunner
from constants import *

class Fruit(MazeRunner):
    def __init__(self, nodes):
        MazeRunner.__init__(self, nodes)
        self.name = "fruit"
        self.color = (0,200,0)
        self.setStartPosition()
        self.lifespan = 5
        self.timer = 0
        self.killme = False

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

    
