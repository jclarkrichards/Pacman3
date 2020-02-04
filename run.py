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
        self.startLabel = Text("START!", RED, 190, 320, 16)
        self.pauseLabel = Text("PAUSED!", RED, 180, 320, 16)
        self.started = False
        self.pausedByPlayer = False
        self.pauseTime = 0
        self.timer = 0
        self.nextLevelAfterPause = False
        self.startAfterPause = False
        self.restartAfterPause = False
        self.flash_background = False
        self.flash_rate = 0.2
        self.flashtime = 0
        self.show_white_background = False
        self.ghost_score = None
        self.fruit_score = None
        self.gameover = False
        
    def setBackground(self):
        self.background = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_white = pygame.surface.Surface(SCREENSIZE).convert()
        self.background.fill(BLACK)

    def startGame(self):
        print("Restarting the game")
        self.maze.setup(self.level)
        self.nodes = NodeGroup(self.maze.filename+".txt")
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.pacman = Pacman(self.nodes, self.sheet)
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.fruit = None
        self.pelletsEaten = 0
        self.lifeIcons = LifeIcon(self.sheet)
        self.maze.stitchMaze(self.background, self.background_white)
        self.hiScoreTxtStatic = Text("HI SCORE", WHITE, 0, 0, 16)
        self.scoreTxtStatic = Text("SCORE", WHITE, 208, 0, 16)
        self.levelTxtStatic = Text("LEVEL", WHITE, 368, 0, 16)
        self.score = 0
        self.scoreLabel = Text(str(self.score).zfill(8), WHITE, 208, 16, 16)
        self.started = False
        self.pausedByPlayer = False
        self.pauseTime = 0
        self.timer = 0
        self.nextLevelAfterPause = False
        self.startAfterPause = False
        self.restartAfterPause = False
        self.flash_background = False
        self.flash_rate = 0.2
        self.flashtime = 0
        self.show_white_background = False
        self.gameover = False
        
    def restartLevel(self):
        print("Restarting the level")
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.started = False
        self.pausedByPlayer = False
        self.fruit = None
        self.pauseTime = 0
        self.timer = 0
        self.nextLevelAfterPause = False
        self.startAfterPause = False
        self.restartAfterPause = False
        self.gameover = False
        self.flash_background = False
        self.flash_rate = 0.2
        self.flashtime = 0
        self.show_white_background = False

    def nextLevel(self):
        self.level += 1
        self.maze.setup(self.level)
        self.nodes = NodeGroup(self.maze.filename+".txt")
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.pacman.updateNodes(self.nodes)
        self.pacman.reset()
        self.ghosts = GhostGroup(self.nodes, self.sheet)
        self.paused = True
        self.started = False
        self.pausedByPlayer = False
        self.fruit = None
        self.pelletsEaten = 0
        self.lifeIcons = LifeIcon(self.sheet)
        self.maze.stitchMaze(self.background, self.background_white)
        self.pellets = PelletGroup(self.maze.filename+".txt")
        self.levelLabel.updateText(str(self.level).zfill(2))
        self.pauseTime = 0
        self.timer = 0
        self.nextLevelAfterPause = False
        self.startAfterPause = False
        self.restartAfterPause = False
        self.gameover = False
        self.flash_background = False
        self.flash_rate = 0.2
        self.flashtime = 0
        self.show_white_background = False
        
    def update(self):
        dt = self.clock.tick(30) / 1000.0
        self.pellets.update(dt)
        if not self.paused:
            self.pacman.update(dt)
            self.ghosts.update(dt, self.pacman)
            if self.fruit is not None:
                self.fruit.update(dt)
        else:
            if not self.pacman.alive:
                print("death sequence")
                self.pacman.updateAnimation(dt)
        self.checkEvents()


        if self.pauseTime > 0:
            self.paused = True
            self.timer += dt
            if self.timer >= self.pauseTime:
                self.paused = False
                self.pauseTime = 0
                self.timer = 0
                self.ghost_score = None
                if self.nextLevelAfterPause:
                    self.nextLevel()
                if self.startAfterPause:
                    self.startGame()
                if self.restartAfterPause:
                    self.restartLevel()
                    
        if self.flash_background:
            self.flashtime += dt
            if self.flashtime >= self.flash_rate:
                self.flashtime = 0
                self.show_white_background = not self.show_white_background

        if self.fruit_score is not None:
            self.fruit_score.update(dt)
            if self.fruit_score.hide:
                self.fruit_score = None

        self.render()

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.started = True
                    self.paused = not self.paused
                    self.pausedByPlayer = self.paused

        if not self.paused:
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
                self.pauseTime = 3
                self.nextLevelAfterPause = True
                self.flash_background = True

    def checkGhostEvents(self):
        self.ghosts.release(self.pelletsEaten)
        ghost = self.pacman.eatGhost(self.ghosts)
        if ghost is not None:
            if ghost.mode.name == "FREIGHT":
                self.pauseTime = 0.5
                self.ghost_score = Text(str(self.ghosts.points), WHITE, ghost.position.x, ghost.position.y, 8)
                ghost.spawnMode()
                self.updateScores(self.ghosts.points)
                self.ghosts.doublePoints()
            elif ghost.mode.name != "SPAWN":
                self.pacman.alive = False
                self.paused = True
                self.pauseTime = 2
                self.pacman.decreaseLives()
                self.gameover = self.pacman.lives == 0
                if self.gameover:
                    print("All of Pacmans lives are gone")
                    self.startAfterPause = True
                else:
                    print("Lost a life, but still going")
                    self.restartAfterPause = True

    def checkFruitEvents(self):
        if self.fruit is not None:
            if self.pacman.eatFruit(self.fruit):
                self.updateScores(self.fruit.points)
                self.trophies.add(self.fruit.name, self.fruit.collect())
                self.fruit_score = Text(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8)
                self.fruit_score.lifespan = 1
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
        if self.show_white_background:
            self.screen.blit(self.background_white, (0,0))
        else:
            self.screen.blit(self.background, (0, 0))
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        if not self.paused or not self.started:
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
        
        if self.pausedByPlayer:
            self.pauseLabel.render(self.screen)
        if not self.started:
            self.startLabel.render(self.screen)

        if self.ghost_score is not None:
            self.ghost_score.render(self.screen)
        if self.fruit_score is not None:
            self.fruit_score.render(self.screen)

        if self.paused and not self.pacman.alive:
            self.pacman.render(self.screen)

        pygame.display.update()



if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
