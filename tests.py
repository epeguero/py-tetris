from tetris import Tetris, Tetromino
import copy

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


if __name__ == "__main__":
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
