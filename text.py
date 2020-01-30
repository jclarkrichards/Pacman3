import pygame
from vector import Vector2
from constants import *

class Text(object): 
    def __init__(self, text, color, x, y, size): 
        self.text = text
        self.color = color
        self.size = size
        self.position = Vector2(x, y)
        self.hide = False
        self.label = None
        self.font = None
        self.totalTime = 0
        self.hasLifespan = False
        self.lifespan = 1
        self.setupFont("PressStart2P.ttf")
        self.createLabel()

    def setupFont(self, fontpath): 
        self.font = pygame.font.Font(fontpath, self.size)

    def createLabel(self): 
        self.label = self.font.render(self.text, 1, self.color)

    def updateText(self, newtext): 
        self.text = newtext
        self.createLabel()

    def update(self, text): 
        if self.hasLifespan: 
            self.totalTime += dt
            if self.totalTime >= self.lifespan: 
                self.totalTime = 0
                self.hide = True
                self.hasLifespan = False

    def render(self, screen): 
        if not self.hide: 
            x, y = self.position.asTuple()
            screen.blit(self.label, (x, y))
