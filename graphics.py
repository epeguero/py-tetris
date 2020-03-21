import curses
from tetris import Tetris

class TetrisGraphicsCurses:
    def __init__(self, screen, row_offset=3, col_offset=3):
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
            self.width, self.height = w, h
            self.drawStartPage()
            self.drawBorders()
        elif Tetris.Output.REMOVE_WELCOME in tetrisOutput:
            self.eraseStartPage()
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

    welcome = -2,0,"WELCOME TO TETRIS!"
    def drawStartPage(self, erase=False):
        row, col, message = self.welcome
        welcomeMessage = message if not erase else " "*len(message)
        self.drawAt(row,col,welcomeMessage)

        moveControlInfo = "  Move:" if not erase else " "*len("  Move:")
        row_off = self.height//4+2
        col_off = self.width//4+2
        self.drawAt(row_off - 2, 0, moveControlInfo)
        self.drawAt(row_off, col_off, "i" if not erase else " ")
        self.drawAt(row_off+1, col_off-1, "j" if not erase else " ")
        self.drawAt(row_off+1, col_off, "k" if not erase else " ")
        self.drawAt(row_off+1, col_off+1, "l" if not erase else " ")

        self.drawAt(row_off+4, 0, "Quit: 'q'" if not erase else " "*len("Quit: 'q'"))

    def eraseStartPage(self):
        self.drawStartPage(erase=True)

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
