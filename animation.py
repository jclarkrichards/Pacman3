class Animation(object): 
    def __init__(self, animType): 
        self.animType = animType
        self.frames = []
        self.col = 0
        self.forward = True
        self.speed = 0
        self.dt = 0

    def addFrame(self, frame): 
        self.frames.append(frame)

    def getFrame(self, dt): 
        if self.animType == "loop": 
            self.loop(dt) 
        elif self.animType == "once": 
            self.onePass(dt) 
        elif self.animType == "ping": 
            self.ping(dt) 
        elif self.animType == "static": 
            self.col = 0 
        return self.frames[self.col]

    def nextFrame(self, dt): 
        self.dt += dt
        if self.dt >= (1.0 / self.speed): 
            if self.forward: 
                self.col += 1 
            else: 
                self.col -= 1 
            self.dt = 0

    def loop(self, dt): 
        self.nextFrame(dt)
        if self.forward: 
            if self.col == len(self.frames): 
                self.col = 0 
        else: 
            if self.col == -1: 
                self.col = len(self.frames) - 1

    def onePass(self, dt): 
        self.nextFrame(dt)
        if self.forward: 
            if self.col == len(self.frames): 
                self.col = len(self.frames) - 1 
        else: 
            if self.col == -1: 
                self.col = 0

    def ping(self, dt): 
        self.nextFrame(dt)
        if self.col == len(self.frames): 
            self.forward = False
            self.col -= 2 
        elif self.col < 0: 
            self.forward = True
            self.col = 1 
