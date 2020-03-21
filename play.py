import curses
from graphics import TetrisGraphicsCurses
from controls import TetrisControlsCurses
from tetris import Tetris

def playTetris(screen):
    graphics = TetrisGraphicsCurses(screen)
    controls = TetrisControlsCurses(screen)
    tetris = Tetris()
    while(tetris.state != Tetris.State.END):
        action = controls.readTetrisAction(tetris.state)
        actionOutput = tetris.action(action)
        tetrisOutput = tetris.update()
        for out in actionOutput,tetrisOutput:
            graphics.update(out)

if __name__ == "__main__":
    curses.wrapper(playTetris)
