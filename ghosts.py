import pygame
from vector import Vector2
from constants import *
from entity import MazeRunner
from random import randint
from modes import Mode
from stack import Stack

class Ghost(MazeRunner):
    def __init__(self, nodes):
        MazeRunner.__init__(self, nodes)
        self.name = "ghost"
        self.goal = Vector2()
        self.modeStack = self.setupModeStack()
        self.mode = self.modeStack.pop()
        self.modeTimer = 0
        self.spawnNode = self.findSpawnNode()
        self.setGuideStack()
        self.bannedDirections = []
        self.setStartPosition()
        self.released = True
        self.pelletsForRelease = 0
        
    def update(self, dt, pacman, blinky):
        speedMod = self.speed * self.mode.speedMult
        self.position += self.direction*speedMod*dt
        self.modeUpdate(dt)
        if self.mode.name == "CHASE":
            self.chaseGoal(pacman, blinky)
        elif self.mode.name == "SCATTER":
            self.scatterGoal()
        elif self.mode.name == "FREIGHT":
            self.randomGoal()
        elif self.mode.name == "SPAWN":
            self.spawnGoal()
        self.moveBySelf()

    def scatterGoal(self):
        self.goal = Vector2(SCREENSIZE[0], 0)

    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position

    def modeUpdate(self, dt):
        self.modeTimer += dt
        if self.mode.time is not None:
            if self.modeTimer >= self.mode.time:
                self.mode = self.modeStack.pop()
                self.modeTimer = 0

    def getValidDirections(self):
        validDirections = []
        for key in self.node.neighbors.keys():
            if self.node.neighbors[key] is not None:
                if key != self.direction * -1:
                    if not self.mode.name == "SPAWN":
                        if not self.node.homeEntrance:
                            if key not in self.bannedDirections:
                                validDirections.append(key)
                        else:
                            if key != DOWN:
                                validDirections.append(key)
                    else:
                        validDirections.append(key)
        if len(validDirections) == 0:
            validDirections.append(self.forceBacktrack())

        return validDirections

    def randomDirection(self, validDirections):
        index = randint(0, len(validDirections) - 1)
        return validDirections[index]

    def moveBySelf(self):
        if self.overshotTarget():
            self.node = self.target
            self.portal()
            validDirections = self.getValidDirections()
            self.direction = self.getClosestDirection(validDirections)
            self.target = self.node.neighbors[self.direction]
            self.setPosition()
            if self.mode.name == "SPAWN":
                if self.position == self.goal:
                    self.mode = Mode("GUIDE", speedMult=0.2)
            if self.mode.name == "GUIDE":
                if self.guide.isEmpty():
                    self.mode = self.modeStack.pop()
                    self.setGuideStack()
                else:
                    self.direction = self.guide.pop()
                    self.target = self.node.neighbors[self.direction]
                    self.setPosition()

    def forceBacktrack(self):
        if self.direction * -1 == UP:
            return UP
        if self.direction * -1 == DOWN:
            return DOWN
        if self.direction * -1 == LEFT:
            return LEFT
        if self.direction * -1 == RIGHT:
            return RIGHT

    def getClosestDirection(self, validDirections):
        distances = []
        for direction in validDirections:
            diffVec = self.node.position + direction*TILEWIDTH - self.goal
            distances.append(diffVec.magnitudeSquared())
        index = distances.index(min(distances))
        return validDirections[index]

    def setupModeStack(self):
        modes = Stack()
        modes.push(Mode(name="CHASE"))
        modes.push(Mode(name="SCATTER", time=5))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        modes.push(Mode(name="CHASE", time=20))
        modes.push(Mode(name="SCATTER", time=7))
        return modes

    def freightMode(self):
        if self.mode.name != "SPAWN":
            if self.mode.name != "FREIGHT":
                if self.mode.time is not None:
                    dt = self.mode.time - self.modeTimer
                    self.modeStack.push(Mode(name=self.mode.name, time=dt))
                else:
                    self.modeStack.push(Mode(name=self.mode.name))
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0
            else:
                self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                self.modeTimer = 0

    def randomGoal(self):
        x = randint(0, NCOLS*TILEWIDTH)
        y = randint(0, NROWS*TILEHEIGHT)
        self.goal = Vector2(x, y)

    def spawnMode(self):
        self.mode = Mode("SPAWN", speedMult=2)
        self.modeTimer = 0

    def findSpawnNode(self):
        for node in self.nodes.homeList:
            if node.spawnNode:
                break
        return node

    def spawnGoal(self):
        self.goal = self.spawnNode.position

    def setGuideStack(self):
        self.guide = Stack()
        self.guide.push(UP)
    
    def findStartNode(self):
        for node in self.nodes.homeList:
            if node.ghostStart:
                return node
        return node

    def setStartPosition(self):
        self.node = self.findStartNode()
        self.target = self.node
        self.setPosition()


class Blinky(Ghost):
    def __init__(self, nodes):
        Ghost.__init__(self, nodes)
        self.name = "blinky"
        self.color = RED


class Pinky(Ghost):
    def __init__(self, nodes):
        Ghost.__init__(self, nodes)
        self.name = "pinky"
        self.color = PINK

    def scatterGoal(self):
        self.goal = Vector2()

    def chaseGoal(self, pacman, blinky=None):
        self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def setStartPosition(self):
        startNode = self.findStartNode()
        self.node = startNode.neighbors[DOWN]
        self.target = self.node
        self.setPosition()

        
class Inky(Ghost):
    def __init__(self, nodes):
        Ghost.__init__(self, nodes)
        self.name = "inky"
        self.color = TEAL
        self.released = False
        self.pelletsForRelease = 30
        
    def scatterGoal(self):
        self.goal = Vector2(TILEWIDTH*NCOLS, TILEHEIGHT*NROWS)

    def chaseGoal(self, pacman, blinky=None):
        vec1 = pacman.position + pacman.direction * TILEWIDTH * 2
        vec2 = (vec1 - blinky.position) * 2
        self.goal = blinky.position + vec2

    def setStartPosition(self):
        self.bannedDirections = [RIGHT]
        startNode = self.findStartNode()
        pinkyNode = startNode.neighbors[DOWN]
        self.node = pinkyNode.neighbors[LEFT]
        self.target = self.node
        self.setPosition()

        
class Clyde(Ghost):
    def __init__(self, nodes):
        Ghost.__init__(self, nodes)
        self.name = "clyde"
        self.color = ORANGE
        self.released = False
        self.pelletsForRelease = 60
        
    def scatterGoal(self):
        self.goal = Vector2(0, TILEHEIGHT*NROWS)

    def chaseGoal(self, pacman, blinky=None):
        d = pacman.position - self.position
        ds = d.magnitudeSquared()
        if ds <= (TILEWIDTH * 8)**2:
            self.scatterGoal()
        else:
            self.goal = pacman.position + pacman.direction * TILEWIDTH * 4

    def setStartPosition(self):
        self.bannedDirections = [LEFT]
        startNode = self.findStartNode()
        pinkyNode = startNode.neighbors[DOWN]
        self.node = pinkyNode.neighbors[RIGHT]
        self.target = self.node
        self.setPosition()

        
class GhostGroup(object):
    def __init__(self, nodes):
        self.nodes = nodes
        self.ghosts = [Blinky(nodes), Pinky(nodes), Inky(nodes), Clyde(nodes)]

    def __iter__(self):
        return iter(self.ghosts)

    def update(self, dt, pacman):
        for ghost in self:
            ghost.update(dt, pacman, self.ghosts[0])

    def freightMode(self):
        for ghost in self:
            ghost.freightMode()

    def release(self, numPelletsEaten):
        for ghost in self:
            if not ghost.released:
                if numPelletsEaten >= ghost.pelletsForRelease:
                    ghost.bannedDirections = []
                    ghost.spawnMode()
                    ghost.released = True
                    
    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
