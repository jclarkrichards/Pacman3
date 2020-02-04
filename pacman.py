import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import MazeRunner
from animation import Animation

class Pacman(MazeRunner):
    def __init__(self, nodes, spritesheet):
        MazeRunner.__init__(self, nodes, spritesheet)
        self.startImage = spritesheet.getImage(4,0,32,32)
        self.image = self.startImage
        self.name = "pacman"
        self.color = YELLOW
        self.setStartPosition()
        self.lives = 5
        self.animation = None
        self.animations = {}
        self.defineAnimations()
        self.alive = True
        self.startDeathAnimation = False
        
    def reset(self):
        self.setStartPosition()
        self.image = self.startImage
        self.alive = True
        self.startDeathAnimation = False
        
    def update(self, dt):
        self.position += self.direction*self.speed*dt
        direction = self.getValidKey()
        if direction:
            self.moveByKey(direction)
        else:
            self.moveBySelf()
        self.updateAnimation(dt)

    def updateAnimation(self, dt):
        if self.alive:
            if self.direction == UP: 
                self.animation = self.animations["up"] 
            elif self.direction == DOWN: 
                self.animation = self.animations["down"] 
            elif self.direction == LEFT: 
                self.animation = self.animations["left"] 
            elif self.direction == RIGHT: 
                self.animation = self.animations["right"] 
            elif self.direction == STOP: 
                self.animation = self.animations["idle"]
        else:
            if not self.startDeathAnimation:
                self.animation = self.animations["death"]
                self.animation.col = 0
                self.startDeathAnimation = True
                
        self.image = self.animation.getFrame(dt) 

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
        
    def defineAnimations(self): 
        anim = Animation("ping")
        anim.speed = 20
        anim.addFrame(self.spritesheet.getImage(4, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(0, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(0, 1, 32, 32))
        self.animations["left"] = anim

        anim = Animation("ping")
        anim.speed = 20
        anim.addFrame(self.spritesheet.getImage(4, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 1, 32, 32))
        self.animations["right"] = anim

        anim = Animation("ping")
        anim.speed = 20
        anim.addFrame(self.spritesheet.getImage(4, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(2, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(2, 1, 32, 32))
        self.animations["down"] = anim

        anim = Animation("ping")
        anim.speed = 20
        anim.addFrame(self.spritesheet.getImage(4, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, 0, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, 1, 32, 32))
        self.animations["up"] = anim

        anim = Animation("once")
        anim.speed = 10
        anim.addFrame(self.spritesheet.getImage(0, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(1, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(2, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(3, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(4, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(5, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(6, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(7, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(8, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(9, 7, 32, 32))
        anim.addFrame(self.spritesheet.getImage(10, 7, 32, 32))
        self.animations["death"] = anim

        anim = Animation("static")
        anim.addFrame(self.spritesheet.getImage(4, 0, 32, 32))
        self.animations["idle"] = anim 


class LifeIcon(object):
    def __init__(self, spritesheet):
        self.width, self.height = 32, 32
        self.image = spritesheet.getImage(0,1,self.width,self.height)
        self.gap = 10
        
    def render(self, screen, num):
        for i in range(num):
            x = self.gap + (self.width + self.gap) * i
            y = TILEHEIGHT * NROWS - self.height
            screen.blit(self.image, (x, y))
