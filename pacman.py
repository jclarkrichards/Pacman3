import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import MazeRunner

class Pacman(MazeRunner):
    def __init__(self, nodes):
        MazeRunner.__init__(self, nodes)
        self.name = "pacman"
        self.color = YELLOW
        self.setStartPosition()
        self.lives = 5

    def reset(self):
        self.setStartPosition()
        
    def update(self, dt):
        self.position += self.direction*self.speed*dt
        direction = self.getValidKey()
        if direction:
            self.moveByKey(direction)
        else:
            self.moveBySelf()

    def getValidKey(self):
        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return None

    def moveByKey(self, direction):
        if self.direction is STOP:
            if self.node.neighbors[direction] is not None:
                self.target = self.node.neighbors[direction]
                self.direction = direction
        else:
            if direction == self.direction * -1:
                self.reverseDirection()
            if self.overshotTarget():
                self.node = self.target
                self.portal()
                if self.node.neighbors[direction] is not None:
                    if self.node.homeEntrance:
                        if self.node.neighbors[self.direction] is not None:
                            self.target = self.node.neighbors[self.direction]
                        else:
                            self.setPosition()
                            self.direction = STOP
                    else:
                        self.target = self.node.neighbors[direction]
                        if self.direction != direction:
                            self.setPosition()
                            self.direction = direction
                else:
                    if self.node.neighbors[self.direction] is not None:
                        self.target = self.node.neighbors[self.direction]
                    else:
                        self.setPosition()
                        self.direction = STOP
                
    def eatPellets(self, pelletList):
        for pellet in pelletList:
            d = self.position - pellet.position
            dSquared = d.magnitudeSquared()
            rSquared = (pellet.radius+self.collideRadius)**2
            if dSquared <= rSquared:
                return pellet
        return None

    def eatGhost(self, ghosts):
        for ghost in ghosts:
            d = self.position - ghost.position
            dSquared = d.magnitudeSquared()
            rSquared = (self.collideRadius + ghost.collideRadius)**2
            if dSquared <= rSquared:
                return ghost
        return None

    def eatFruit(self, fruit):
        d = self.position - fruit.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius+fruit.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False
    
    def findStartNode(self):
        for node in self.nodes.nodeList:
            if node.pacmanStart:
                return node
        return node

    def setStartPosition(self):
        self.direction = LEFT
        self.node = self.findStartNode()
        self.target = self.node.neighbors[self.direction]
        self.setPosition()
        self.position.x -= (self.node.position.x - self.target.position.x) / 2

    def decreaseLives(self):
        self.lives -= 1
        if self.lives == 0:
            return True
        return False



class LifeIcon(object):
    def __init__(self):
        self.image = pygame.image.load("Images/pacman_single.png").convert()
        self.image.set_colorkey(TRANSPARENT)
        self.width, self.height = self.image.get_size()
        self.gap = 10

    def render(self, screen, num):
        for i in range(num):
            x = self.gap + (self.width + self.gap) * i
            y = TILEHEIGHT * NROWS - self.height
            screen.blit(self.image, (x, y))
