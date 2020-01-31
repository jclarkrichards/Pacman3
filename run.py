import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman, LifeIcon
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit, FruitTrophy
from sprites import Spritesheet
from maze import Maze
from text import Text

class GameController(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, 0, 32)
        self.background = None
        self.setBackground()
        self.clock = pygame.time.Clock()
        self.hiscore = 0
        self.hiscoreLabel = Text(str(self.hiscore).zfill(8), WHITE, 0, 16, 16)
        self.level = 1
        self.levelLabel = Text(str(self.level).zfill(2), WHITE, 368, 16, 16)
        self.sheet = Spritesheet()
        self.maze = Maze(self.sheet)
        self.trophies = FruitTrophy()
        
    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        self.maze.setup(self.level)
        self.nodes = NodeGroup(self.maze.filename+".txt")
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.pacman = Pacman(self.nodes, self.sheet)
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.fruit = None
        self.pelletsEaten = 0
        self.lifeIcons = LifeIcon(self.sheet)
        self.maze.stitchMaze(self.background)
        self.hiScoreTxtStatic = Text("HI SCORE", WHITE, 0, 0, 16)
        self.scoreTxtStatic = Text("SCORE", WHITE, 208, 0, 16)
        self.levelTxtStatic = Text("LEVEL", WHITE, 368, 0, 16)
        self.score = 0
        self.scoreLabel = Text(str(self.score).zfill(8), WHITE, 208, 16, 16)
        
    def restartLevel(self):
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.fruit = None

    def nextLevel(self):
        self.level += 1
        self.maze.setup(self.level)
        self.nodes = NodeGroup(self.maze.filename+".txt")
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.pacman.updateNodes(self.nodes)
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.fruit = None
        self.pelletsEaten = 0
        self.lifeIcons = LifeIcon(self.sheet)
        self.maze.stitchMaze(self.background)
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.levelLabel.updateText(str(self.level).zfill(2))
        
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
            self.updateScores(pellet.points)
            self.ghosts.resetPoints()
            if (self.pelletsEaten == 70 or self.pelletsEaten == 140):
                if self.fruit is None:
                    self.fruit = Fruit(self.nodes, self.sheet, self.level)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == "powerpellet":
                self.ghosts.freightMode()
            if self.pellets.isEmpty():
                self.nextLevel()

    def checkGhostEvents(self):
        self.ghosts.release(self.pelletsEaten)
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                ghost.spawnMode()
                self.updateScores(self.ghosts.points)
                self.ghosts.doublePoints()
            elif ghost.mode.name != "SPAWN":
                if self.pacman.decreaseLives():
                    self.startGame()
                else:
                    self.restartLevel()

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit):
                self.updateScores(self.fruit.points)
                self.trophies.add(self.fruit.name, self.fruit.collect())
                self.fruit = None
            else:
                if self.fruit.killme:
                    self.fruit = None

    def updateScores(self, value): 
        self.score += value
        self.scoreLabel.updateText(str(self.score).zfill(8))
        if self.score > self.hiscore: 
            self.hiscore = self.score
            self.hiscoreLabel.updateText(str(self.hiscore).zfill(8))

    def render(self):
        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.lifeIcons.render(self.screen, self.pacman.lives-1)
        self.hiScoreTxtStatic.render(self.screen)
        self.scoreTxtStatic.render(self.screen)
        self.levelTxtStatic.render(self.screen)
        self.scoreLabel.render(self.screen)
        self.hiscoreLabel.render(self.screen)
        self.levelLabel.render(self.screen)
        self.trophies.render(self.screen)
        pygame.display.update()



if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
