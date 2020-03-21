import curses
import random
import time
import copy
from enum import Enum

class TetrisGraphicsCurses:
    def __init__(self, screen, row_offset, col_offset):
        self.prevTetro = None
        self.screen = screen
        self.row_offset = min(row_offset, 3)
        self.col_offset = min(col_offset, 3)
        self.width = None
        self.height = None

        # curses init colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.screen.nodelay(1)

    def exit(self):
        self.screen.clear()
        self.screen.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def readInput(self):
        return graphics.screen.getch()

    def update(self, tetrisOutput):
        if tetrisOutput == None:
            return
        if Tetris.Output.WELCOME in tetrisOutput:
            _,w,h = tetrisOutput
            self.drawAt(-2, 0, "WELCOME TO TETRIS!")
            self.width, self.height = w, h
            self.drawBorders()
        elif Tetris.Output.MATERIALIZE in tetrisOutput:
            _,tetro = tetrisOutput
            self.drawTetro(tetro)
            self.prevTetro = tetro
        elif Tetris.Output.MOVE in tetrisOutput:
            _,currTetro = tetrisOutput
            self.eraseTetro(self.prevTetro)
            self.drawTetro(currTetro)
            self.prevTetro = currTetro
        elif Tetris.Output.LINE_CLEAR in tetrisOutput:
            _,clearedLines = tetrisOutput
            for l in clearedLines:
                self.clearLine(l)
        elif Tetris.Output.ROTATE in tetrisOutput:
            _,tetro = tetrisOutput
            self.eraseTetro(self.prevTetro)
            self.drawTetro(tetro)
            self.prevTetro = tetro


    def drawBorders(self):
        # draw sides
        for i in range(self.height):
            self.drawAt(i, -1, "#")
            self.drawAt(i, self.width, "#")

        #draw bottom
        for i in range(-1,self.width+1):
            self.drawAt(self.height, i, "#")


    def clearLine(self, line):
        self.screen.move(self.row_offset+line,0)
        self.screen.deleteln()
        self.screen.move(self.row_offset-1,0)
        self.screen.insertln()
        self.screen.refresh()
        self.drawBorders()

    def drawTetro(self, tetro, char="\u25a0"):
        color = self.tetroColor(tetro.tetroKind)
        for i in range(len(tetro.map)):
            for j in range(len(tetro.map[i])):
                if tetro.map[i][j] != 0:
                    self.drawAt(tetro.row + i,
                                tetro.col + j, char, color)


    def eraseTetro(self, tetro):
        self.drawTetro(tetro," ")

    def drawAt(self, row, col, char, color=None):
        color = (curses.color_pair(1)
                    if color == None
                    else color)
        # +1 accounts for side of board
        self.screen.addstr(row+self.row_offset,
                        col+self.col_offset+1, char, color)
        self.screen.refresh()

    def tetroColor(self, tetroKind):
        if tetroKind == Tetris.TetrominoKind.J:
            return curses.color_pair(5)
        elif tetroKind == Tetris.TetrominoKind.L:
            return curses.color_pair(7)
        elif tetroKind == Tetris.TetrominoKind.S:
            return curses.color_pair(2)
        elif tetroKind == Tetris.TetrominoKind.Z:
            return curses.color_pair(3)
        elif tetroKind == Tetris.TetrominoKind.I:
            return curses.color_pair(9)
        elif tetroKind == Tetris.TetrominoKind.O:
            return curses.color_pair(4)



class TetrisControlsCurses:
    def __init__(self, screen):
        self.screen = screen

    def readTetrisAction(self):
        key = self.screen.getch()
        if key > 0:
            if chr(key) == 'q':
                return Tetris.Action.QUIT
            elif key in [curses.KEY_LEFT, ord('j')]:
                return Tetris.Action.LEFT
            elif key in [curses.KEY_RIGHT, ord('l')]:
                return Tetris.Action.RIGHT
            elif key in [curses.KEY_DOWN, ord('k')]:
                return Tetris.Action.DOWN
            elif key in [curses.KEY_UP, ord('i')]:
                return Tetris.Action.ROTATE
            elif chr(key) == ' ':
                return Tetris.Action.DROP
        return None


import numpy
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
        self.state = Tetris.State.MATERIALIZE
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



def playTetris(screen):
    graphics = TetrisGraphicsCurses(screen, 3,3)
    controls = TetrisControlsCurses(screen)
    tetris = Tetris()
    while(tetris.state != Tetris.State.END):
        action = controls.readTetrisAction()
        actionOutput = tetris.action(action)
        tetrisOutput = tetris.update()
        for out in actionOutput,tetrisOutput:
            graphics.update(out)



def fallAfterMaterialize():
    tetris = Tetris(10,20)
    tetris.state = Tetris.State.MATERIALIZE
    tetris.update()
    assert(tetris.state == Tetris.State.FALLING)

def fallActuallyFalls():
    tetris = Tetris(20, 10)
    tetris.state == Tetris.State.FALLING
    tetro0 = Tetromino(0, 0, Tetris.TetrominoKind.O)
    tetris.tetro = copy.copy(tetro0)
    tetro1 = tetris.tetro

    tetris.moveDown(1)

    assert(tetro0.tetroKind == tetro1.tetroKind)
    assert(tetro0.col== tetro1.col)
    assert(tetro0.row+1== tetro1.row)

def placeAfterFallingEnough():
    tetris = Tetris()
    tetris.state = Tetris.State.FALLING
    tetris.tetro = Tetromino(0, 0, Tetris.TetrominoKind.Z)
    tetris.moveDown(tetris.height)
    assert(tetris.state == Tetris.State.FALLING)
    tetris.moveDown(1)
    assert(tetris.state == Tetris.State.PLACE)

def placeSavesTetromino():
    width = 4
    height = 4
    tetroKind = Tetris.TetrominoKind.O
    tetroWidth = 2
    tetroHeight = 2
    tetris = Tetris(width, height)
    tetris.tetro = Tetromino(2,0,tetroKind)
    tetris.state = Tetris.State.PLACE

    o = tetroKind.value
    correctGrid = [ [0,0,0,0],
                    [0,0,0,0],
                    [o,o,0,0],
                    [o,o,0,0] ]

    tetris.place()

    assert(tetris.grid == correctGrid)

def materializeNewTetrominoAfterPlace():
    tetris = Tetris(10,10)
    tetris.state = Tetris.State.PLACE
    tetris.tetro = Tetromino(0,5, Tetris.TetrominoKind.O)
    tetris.place()
    assert(tetris.state == Tetris.State.MATERIALIZE)
    tetris.materialize()
    assert(tetris.tetro.row == 0)

def quitActionActuallyQuits():
    tetris = Tetris(10,10)
    assert(tetris.state != Tetris.State.END)
    tetris.action(Tetris.Action.QUIT)
    assert(tetris.state == Tetris.State.END)

def dropToGroundWorks():
    initRow = 0
    initCol = 0
    tetro = Tetromino(initRow, initCol, Tetris.TetrominoKind.O)
    o = tetro.tetroKind.value
    initialGrid = [ [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [o,o,0,0],
                    [o,o,0,0] ]
    expectedGrid = [ [0,0,0,0],
                     [o,o,0,0],
                     [o,o,0,0],
                     [o,o,0,0],
                     [o,o,0,0] ]
    height = 5
    width = 4
    tetris = Tetris(height, width)
    tetris.tetro = tetro
    tetris.grid = initialGrid

    tetris.drop()

    finalRow, finalCol = (tetris.tetro.row,
                         tetris.tetro.col)
    assert((finalRow,finalCol) == (1,initCol))

    tetris.place()
    assert(tetris.grid == expectedGrid)

def collisionAllowsFullDrop():
    initRow = 0
    initCol = 0
    tetro = Tetromino(initRow, initCol, Tetris.TetrominoKind.Z)
    tetro.rotate()
    z = tetro.tetroKind.value
    initialGrid = [ [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,z,0,0],
                    [z,z,0,0],
                    [z,0,0,0] ]
    expectedGrid =    [ [0,0,0,0],
                        [0,z,0,0],
                        [z,z,0,0],
                        [z,z,0,0],
                        [z,z,0,0],
                        [z,0,0,0] ]
    height = 6
    width = 4
    tetris = Tetris(height, width)
    tetris.tetro = tetro
    tetris.grid = initialGrid

    tetris.drop()

    finalRow, finalCol = (tetris.tetro.row,
                         tetris.tetro.col)
    assert((finalRow,finalCol) == (1,initCol))

    tetris.place()
    assert(tetris.grid == expectedGrid)

def lineClearingLogicIsCorrect():
    tetris = Tetris(5,4)
    i = Tetris.TetrominoKind.I.value
    initialGrid = [ [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [i,i,i,i] ]
    expectedGrid = [ [0,0,0,0],
                     [0,0,0,0],
                     [0,0,0,0],
                     [0,0,0,0],
                     [0,0,0,0] ]

    tetris.grid = initialGrid
    assert(tetris.rowIsFull(4))
    tetris.clearLine(4)
    assert(tetris.grid == expectedGrid)

def lineClearIntegrationTest():
    height = 5
    width = 4
    tetris = Tetris(height, width)
    tetris.tetro = Tetromino(height-1,0,Tetris.TetrominoKind.I)
    tetris.state = Tetris.State.PLACE

    out = tetris.update()

    assert(out != None and Tetris.Output.LINE_CLEAR in out)
    _, clearedLines = out
    assert(clearedLines == [4])

def visualTest(screen):
    graphics = TetrisGraphicsCurses(screen,0,0)
    tetro = Tetromino(0,0,Tetris.TetrominoKind.S)
    graphics.drawTetro(tetro)
    for i in range(100000):
        graphics.screen.refresh()
    graphics.eraseTetro(tetro)
    for i in range(100000):
        graphics.screen.refresh()
    graphics.exit()


testing = True
running = True
if __name__ == "__main__":
    if testing:
        fallAfterMaterialize()
        fallActuallyFalls()
        placeAfterFallingEnough()
        materializeNewTetrominoAfterPlace()
        placeSavesTetromino()
        quitActionActuallyQuits()
        dropToGroundWorks()
        lineClearingLogicIsCorrect()
        lineClearIntegrationTest()
        collisionAllowsFullDrop()

        print("ALL TESTS PASS!")

    if running:
        # curses.wrapper(visualTest)
        curses.wrapper(playTetris)
        print("Thank you so much for-a playing my game!")
