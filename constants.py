from vector import Vector2

TILEWIDTH = 16
TILEHEIGHT = 16
NROWS = 36
NCOLS = 28
SCREENSIZE = (NCOLS*TILEWIDTH, NROWS*TILEHEIGHT)

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

UP = Vector2(0, -1)
DOWN = Vector2(0, 1)
LEFT = Vector2(-1, 0)
RIGHT = Vector2(1, 0)
STOP = Vector2()
