import numpy as np
import cv2


class GoGame:

    def __init__(self, game_size=19, handicap=None, rule='Zhongguo'):
        assert game_size in [9, 13, 19]
        assert rule in ['zhongguo', 'yingshi', 'hanguo', 'ribeng']
        self.game_size = game_size - 1
        self.game_board = np.zeros(shape=(game_size, game_size), dtype=np.int8)
        self.boardered =
        self.game_history = []
        self.player = 1 # black goes
        self.rule = rule
        if handicap:
            self.handicap = []
            self.player = 2 # white goes first when handicap

    def add_boarder(self):
        # this method give boader to the game_board matrix
        vertical = np.ones(shape=(1, self.game_size), dtype=np.int8)
        self.boardered = np.stack((3 * vertical, self.game_board, 3 * vertical), axis=1)
        horizontal = np.ones(shape=(1, self.game_size + 2))
        self.boardered = np.stack((3 * horizontal, self.boardered, 3 * horizontal), axis=0)
        return self.boardered

    def switch_side(self):
        if self.player == 1:
            self.player = 2
        if self.player == 2:
            self.player = 1

    def place_stone(self, location: (int, int)):
        assert 0 <= location[0] < self.game_size
        assert 0 <= location[1] < self.game_size
        assert self.game_board[location[0]][location[1]] == 0
        self.game_board[location[0]][location[1]] = self.player
        self.switch_side()
        self.game_history.append(self.game_board)
        return self.game_board

    def si_huo(self, last_play: (int, int)):
        pass

    def qi(self, x, y):
        # 判断每个子有没有气， 有气返回1， 没气返回0
        if any([self.boardered[x - 1][y], self.boardered[x + 1][y], self.boardered[x][y + 1], self.boardered[x][y - 1]]):
            return 1
        else:
            return 0

