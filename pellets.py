import pygame
from vector import Vector2
from constants import *

class Pellet(object):
    def __init__(self, x, y):
        self.name = "pellet"
        self.position = Vector2(x, y)
        self.color = YELLOW
        self.radius = 2
        self.points = 10

    def render(self, screen):
        p = self.position.asInt()
        p = (int(p[0]+TILEWIDTH/2), int(p[1]+TILEWIDTH/2))
        pygame.draw.circle(screen, self.color, p, self.radius)


class PowerPellet(Pellet):
    def __init__(self, x, y):
        Pellet.__init__(self, x, y)
        self.name = "powerpellet"
        self.radius = 8
        self.points = 50


class PelletGroup(object):
    def __init__(self, mazefile):
        self.pelletList = []
        self.pelletSymbols = ["p", "n"]
        self.powerpelletSymbols = ["P", "N"]
        self.createPelletList(mazefile)

    def createPelletList(self, mazefile):
        grid = self.readMazeFile(mazefile)
        rows = len(grid)
        cols = len(grid[0])
        for row in range(rows):
            for col in range(cols):
                if (grid[row][col] in self.pelletSymbols):
                    self.pelletList.append(Pellet(col*TILEWIDTH, row*TILEHEIGHT))
                if (grid[row][col] in self.powerpelletSymbols):
                    self.pelletList.append(PowerPellet(col*TILEWIDTH, row*TILEHEIGHT))

    def readMazeFile(self, textfile):
        f = open(textfile, "r")
        lines = [line.rstrip('\n') for line in f]
        return [line.split(' ') for line in lines]

    def isEmpty(self):
        if len(self.pelletList) == 0:
            return True
        return False

    def render(self, screen):
        for pellet in self.pelletList:
            pellet.render(screen)
