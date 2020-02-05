import pygame
from vector import Vector2
from constants import *
from entity import MazeRunner
from random import randint
from modes import Mode
from stack import Stack
from animation import Animation

class Ghost(MazeRunner):
    def __init__(self, nodes, spritesheet):
        MazeRunner.__init__(self, nodes, spritesheet)
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
        self.animation = None
        self.animations = {}
        self.free = True
        
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
        self.portalSlowdown()
        self.updateAnimation(dt)
        if self.name == "pinky":
            print(self.mode.name)
            
    def updateAnimation(self, dt):
        if self.mode.name in ["CHASE", "SCATTER", "GUIDE"]:
            if self.direction == UP: 
                self.animation = self.animations["up"] 
            elif self.direction == DOWN: 
                self.animation = self.animations["down"] 
            elif self.direction == LEFT: 
                self.animation = self.animations["left"] 
            elif self.direction == RIGHT: 
                self.animation = self.animations["right"] 
        elif self.mode.name == "FREIGHT":
            if self.modeTimer < (self.mode.time - 2):
                self.animation = self.animations["freight"]
            else:
                self.animation = self.animations["flash"]
                
        elif self.mode.name == "SPAWN":
            if self.free:
                if self.direction == UP: 
                    self.animation = self.animations["spawnup"] 
                elif self.direction == DOWN: 
                    self.animation = self.animations["spawndown"] 
                elif self.direction == LEFT: 
                    self.animation = self.animations["spawnleft"] 
                elif self.direction == RIGHT: 
                    self.animation = self.animations["spawnright"]
            else:
                if self.direction == UP: 
                    self.animation = self.animations["up"] 
                elif self.direction == DOWN: 
                    self.animation = self.animations["down"] 
                elif self.direction == LEFT: 
                    self.animation = self.animations["left"] 
                elif self.direction == RIGHT: 
                    self.animation = self.animations["right"] 
                
        self.image = self.animation.getFrame(dt)

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
                self.reverseDirection()
                
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

    def portalSlowdown(self):
        self.speed = 100
        if self.node.portalNode or self.target.portalNode:
            self.speed = 50
    
    def moveBySelf(self):
        if self.overshotTarget():
            self.node = self.target
            self.portal()
            validDirections = self.getValidDirections()
            self.direction = self.getClosestDirection(validDirections)
            self.target = self.node.neighbors[self.direction]
            self.setPosition()
            if self.mode.name == "SPAWN":
                if self.node.homeEntrance: print("GOING TOWARDS MY HOMIE")
                if self.position == self.goal:
                    self.mode = Mode("GUIDE", speedMult=0.5)
            if self.mode.name == "GUIDE":
                if self.guide.isEmpty():
                    self.mode = self.modeStack.pop()
                    self.setGuideStack()
                    self.free = True
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
        if self.released:
            #self.reverseDirection()#######
            #print("FREIGHT")#########
            if self.mode.name != "SPAWN":
                if self.mode.name != "FREIGHT": #In SCATTER, CHASE, or GUIDE
                    if self.mode.name != "GUIDE":
                        self.reverseDirection()
                    if self.mode.time is not None:
                        dt = self.mode.time - self.modeTimer
                        self.modeStack.push(Mode(name=self.mode.name, time=dt))
                    else:
                        self.modeStack.push(Mode(name=self.mode.name))
                    self.mode = Mode("FREIGHT", time=7, speedMult=0.5)
                    self.modeTimer = 0
                else: #already in FREIGHT mode, so just reset the mode
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

    def defineAnimations(self, row): 
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, row, 32, 32))
        self.animations["up"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(2, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, row, 32, 32))
        self.animations["down"] = anim

        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(5, row, 32, 32))
        self.animations["left"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, row, 32, 32))
        anim.addFrame(self.spritesheet.getImage(7, row, 32, 32))
        self.animations["right"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 6, 32, 32))
        self.animations["freight"] = anim
        
        anim = Animation("loop")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(2, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 6, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, 6, 32, 32))
        self.animations["flash"] = anim
        
        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(4, 6, 32, 32))
        self.animations["spawnup"] = anim
        
        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(5, 6, 32, 32))
        self.animations["spawndown"] = anim
        
        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(6, 6, 32, 32))
        self.animations["spawnleft"] = anim
        
        anim = Animation("static")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(7, 6, 32, 32))
        self.animations["spawnright"] = anim

        
class Blinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.image = self.spritesheet.getImage(4,2,32,32)
        self.defineAnimations(2)
        self.name = "blinky"
        self.color = RED

        
class Pinky(Ghost):
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.image = self.spritesheet.getImage(0,3,32,32)
        self.defineAnimations(3)
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
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.image = self.spritesheet.getImage(2,4,32,32)
        self.defineAnimations(4)
        self.name = "inky"
        self.color = TEAL
        self.released = False
        self.free = False
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
    def __init__(self, nodes, spritesheet):
        Ghost.__init__(self, nodes, spritesheet)
        self.image = self.spritesheet.getImage(2,5,32,32)
        self.defineAnimations(5)
        self.name = "clyde"
        self.color = ORANGE
        self.released = False
        self.free = False
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
    def __init__(self, nodes, spritesheet):
        self.nodes = nodes
        self.ghosts = [Blinky(nodes, spritesheet),
                       Pinky(nodes, spritesheet),
                       Inky(nodes, spritesheet),
                       Clyde(nodes, spritesheet)]
        self.points = 200
        
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

    def resetPoints(self):
        self.points = 200

    def doublePoints(self):
        self.points *= 2
        
    def render(self, screen):
        for ghost in self:
            ghost.render(screen)
