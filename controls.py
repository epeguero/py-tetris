import curses
from tetris import Tetris

class TetrisControlsCurses:
    def __init__(self, screen):
        self.screen = screen

    def readTetrisAction(self, state):
        key = self.screen.getch()
        if key > 0:
            if state == Tetris.State.START:
                return Tetris.Action.START_GAME

            elif chr(key) == 'q':
                return Tetris.Action.QUIT

            elif state == Tetris.State.FALLING:
                if key in [curses.KEY_LEFT, ord('j')]:
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


