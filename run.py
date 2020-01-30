import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman, LifeIcon
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.setBackground()
        self.clock = pygame.time.Clock()
        
    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        self.nodes = NodeGroup("maze1.txt")
        self.pellets = PelletGroup("maze1.txt")
        self.pacman = Pacman(self.nodes)
        self.ghosts = GhostGroup(self.nodes)
        self.paused = True
        self.fruit = None
        self.pelletsEaten = 0
        self.lifeIcons = LifeIcon()
        
    def restartLevel(self):
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes)
        self.paused = True
        self.fruit = None
        
    def update(self):
        dt = self.clock.tick(30) / 1000.0
        if not self.paused:
            self.pacman.update(dt)
            self.ghosts.update(dt, self.pacman)
            if self.fruit is not None:
                self.fruit.update(dt)
        self.checkEvents()
        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.paused = not self.paused
        self.checkPelletEvents()
        self.checkGhostEvents()
        self.checkFruitEvents()
        
    def checkPelletEvents(self):
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pelletsEaten += 1
            if (self.pelletsEaten == 70 or self.pelletsEaten == 140):
                if self.fruit is None:
                    self.fruit = Fruit(self.nodes)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == "powerpellet":
                self.ghosts.freightMode()
            if self.pellets.isEmpty():
                self.startGame()

    def checkGhostEvents(self):
        self.ghosts.release(self.pelletsEaten)
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                ghost.spawnMode()
            elif ghost.mode.name != "SPAWN":
                if self.pacman.decreaseLives():
                    self.startGame()
                else:
                    self.restartLevel()

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit) or self.fruit.killme:
                self.fruit = None
                
    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.lifeIcons.render(self.screen, self.pacman.lives-1)
        pygame.display.update()



if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
