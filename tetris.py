import curses
import numpy
import random
import time
import copy
from enum import Enum

class Tetris:
    class State(Enum):
        START = 0
        MATERIALIZE = 1
        FALLING = 2
        PLACE = 3
        END = 4

    class Output(Enum):
        WELCOME = 0
        MATERIALIZE = 1
        MOVE = 2
        LINE_CLEAR = 3
        ROTATE = 4
        REMOVE_WELCOME = 5

    class TetrominoKind(Enum):
        J = 1
        L = 2
        S = 3
        Z = 4
        I = 5
        O = 6

    class Action(Enum):
        QUIT = 0
        LEFT = 1
        RIGHT = 2
        DOWN = 3
        DROP = 4
        ROTATE = 5
        START_GAME = 6

    def __init__(self, height=20, width=10):
        self.width = width
        self.height = height
        self.state = Tetris.State.START
        self.tetro = None
        self.grid = [[0 for _ in range(width)]
                        for _ in range(height)]
        self.timeSinceLastFall = 0
        self.prevTime = time.time()
        self.fallDelay = 0.5

    def action(self, action):
        if action == Tetris.Action.QUIT:
            self.state = Tetris.State.END

        elif self.state == Tetris.State.START:
            if action == Tetris.Action.START_GAME:
                self.state = Tetris.State.MATERIALIZE
                return [Tetris.Output.REMOVE_WELCOME]

        elif self.state == Tetris.State.FALLING:
            if action == Tetris.Action.LEFT:
                return self.moveHor(-1)
            elif action == Tetris.Action.RIGHT:
                return self.moveHor(1)
            elif action == Tetris.Action.DOWN:
                return self.moveDown(1)
            elif action == Tetris.Action.DROP:
                return self.drop()
            elif action == Tetris.Action.ROTATE:
                return self.rotate()
        return None

    def drop(self):
        self.state = Tetris.State.PLACE
        return self.moveDown(self.height)

    def rotate(self):
        #TODO: don't let rotation break through borders
        self.tetro.rotate()
        return Tetris.Output.ROTATE, copy.copy(self.tetro)

    def update(self):
        if self.state == Tetris.State.START:
            return self.start()
        elif self.state == Tetris.State.MATERIALIZE:
            return self.materialize()
        elif self.state == Tetris.State.FALLING:
            return self.timed_fall()
        elif self.state == Tetris.State.PLACE:
            return self.place()

    def start(self):
        return Tetris.Output.WELCOME, self.width, self.height

    def materialize(self):
        t = random.choice(list(Tetris.TetrominoKind))
        # t = Tetris.TetrominoKind.S
        self.tetro = Tetromino(0, 0, t)
        self.state = Tetris.State.FALLING
        return Tetris.Output.MATERIALIZE, copy.copy(self.tetro)

    def timed_fall(self):
        currTime = time.time()
        deltaT = time.time() - self.prevTime
        self.prevTime = currTime
        self.timeSinceLastFall += deltaT
        if self.timeSinceLastFall > self.fallDelay:
            self.timeSinceLastFall = 0
            return self.moveDown(1)
        return None

    def moveDown(self, rowDelta):
        oldRow = self.tetro.row

        fallAmount = 0
        while(fallAmount < rowDelta and
                not self.collides(self.tetro.map,
                                self.grid,
                                oldRow+fallAmount+1,
                                self.tetro.col)):
            fallAmount += 1

        self.tetro.row = oldRow + fallAmount

        if fallAmount == 0:
            self.state = Tetris.State.PLACE
            return None
        else:
            return Tetris.Output.MOVE, copy.copy(self.tetro)

    def moveHor(self, colDelta):
        moveCol = (lambda col:
            col + (1 if colDelta >=0 else -1))
        moveAmount = 0
        currCol = self.tetro.col
        while(not self.collides(self.tetro.map,
                                self.grid,
                                self.tetro.row,
                                moveCol(currCol))
              and moveAmount < abs(colDelta)):
            currCol = moveCol(currCol)
            moveAmount += 1

        if moveAmount > 0:
            self.tetro.col = currCol
            return Tetris.Output.MOVE, copy.copy(self.tetro)
        else:
            return None


    def place(self):
        self.insertIntoGrid(self.tetro)
        rowsToCheck = list(range(
            self.tetro.row,
            self.tetro.row+self.tetro.tetroHeight))
        rowsToClear = [row for row in rowsToCheck
                            if self.rowIsFull(row)]
        self.state = Tetris.State.MATERIALIZE
        for l in rowsToClear: self.clearLine(l)
        return ((Tetris.Output.LINE_CLEAR, rowsToClear)
                    if len(rowsToClear) > 0
                    else None)

    def insertIntoGrid(self, t):
        map = t.map
        for i in range(len(map)):
            for j in range(len(map[i])):
                if map[i][j] != 0:
                    self.grid[t.row + i][t.col + j] = (
                        t.tetroKind.value)

    def clearLine(self, l):
        del(self.grid[l])
        emptyRow = [0] * self.width
        self.grid.insert(0,emptyRow)

    def rowIsFull(self,row):
        for col in range(self.width):
            if self.grid[row][col] == 0:
                return False
        return True

    def collides(self, obj, world, world_row, world_col):
        obj_length = len(obj)
        obj_width = len(obj[0])
        world_length = len(world)
        world_width = len(world[0])
        if (world_row + obj_length > world_length or
            world_col + obj_width > world_width or
            world_row < 0 or world_col < 0 or
            world_row >= world_length or
            world_col >= world_width):
            return True
        for i in range(len(obj)):
            for j in range(len(obj[i])):
                if (world[world_row+i][world_col+j] != 0 and
                    obj[i][j] != 0):
                    return True
        return False

class Tetromino:
    def __init__(self, row, col, tetroKind):
        self.row = row
        self.col = col
        self.tetroKind = tetroKind
        self.map = self.default_map(tetroKind)
        if tetroKind == Tetris.TetrominoKind.I:
            self.tetroHeight = 1
            self.tetroWidth = 4
        elif tetroKind == Tetris.TetrominoKind.O:
            self.tetroHeight = 2
            self.tetroWidth = 2
        else:
            self.tetroHeight = 2
            self.tetroWidth = 3

    def rotate(self):
        self.map = numpy.rot90(self.map)
        tmp = self.tetroHeight
        self.tetroHeight = self.tetroWidth
        self.tetroWidth = tmp

    def default_map(self, tetroKind):
        v = tetroKind.value
        if self.tetroKind == Tetris.TetrominoKind.J:
            return [ [v, 0, 0],
                     [v, v, v]]
        elif self.tetroKind == Tetris.TetrominoKind.L:
            return [ [v, v, v],
                     [v, 0, 0]]
        elif self.tetroKind == Tetris.TetrominoKind.S:
            return [ [0, v, v],
                     [v, v, 0]]
        elif self.tetroKind == Tetris.TetrominoKind.Z:
            return [ [v, v, 0],
                     [0, v, v]]
        elif self.tetroKind == Tetris.TetrominoKind.I:
            return [ [v, v, v, v] ]
        elif self.tetroKind == Tetris.TetrominoKind.O:
            return [ [v, v],
                     [v, v] ]


