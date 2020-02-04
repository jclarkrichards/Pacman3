import pygame
from constants import *

class Maze(object): 
    def __init__(self, spritesheet):
        self.defineMazes()
        self.spritesheet = spritesheet
        self.mazeInfo = None
        self.rotateInfo = None
        self.images = []
        self.imageRow = 16
        self.getMazeImages()
        
    def defineMazes(self):
        self.mazes = {}
        self.mazes[0] = {"filename":"maze1", "row":16}
        self.mazes[1] = {"filename":"maze1", "row":17}
        self.mazes[2] = {"filename":"maze1", "row":18}
    
    def setup(self, level):
        index = (level-1) % len(self.mazes)
        self.filename = self.mazes[index]["filename"]
        self.imageRow = self.mazes[index]["row"]
        self.images = self.getMazeImages()
        self.images_flash = self.getMazeImages(11)
        self.getMaze(self.filename)
        
    def getMazeImages(self, offset=0):
        images = []
        for i in range(10): 
            images.append(self.spritesheet.getImage(i+offset, self.imageRow, TILEWIDTH, TILEHEIGHT))
        return images

    def rotate(self, image, value): 
        return pygame.transform.rotate(image, value*90)

    def readMazeFile(self, textfile): 
        f = open(textfile, "r")
        lines = [line.rstrip('\n') for line in f]
        return [line.split(' ') for line in lines]

    def getMaze(self, txtfile): 
        self.mazeInfo = self.readMazeFile(txtfile+".txt")
        self.rotateInfo = self.readMazeFile(txtfile+"_rot.txt")

    def stitchMaze(self, background, background_flash):
        rows = len(self.mazeInfo)
        cols = len(self.mazeInfo[0])
        
        for row in range(rows): 
            for col in range(cols): 
                x = col * TILEWIDTH
                y = row * TILEHEIGHT
                try: 
                    val = int(self.mazeInfo[row][col]) 
                except ValueError: 
                    pass 
                else: 
                    if self.rotateInfo is not None: 
                        rotVal = self.rotateInfo[row][col]
                        image = self.rotate(self.images[val], int(rotVal))
                        image_flash = self.rotate(self.images_flash[val], int(rotVal))
                        background.blit(image, (x, y))
                        background_flash.blit(image_flash, (x, y))
                    else: 
                        background.blit(self.images[val], (x, y))
                        background_flash.blit(self.images_flash[val], (x, y))
