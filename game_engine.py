import numpy as np


class GoGame:

    def __init__(self, game_size=19, handicap=None, rule='weiqi'):

        # assert game_size in [9, 13, 19]
        assert rule in ['weiqi', 'wuzi']

        self.end_game = False
        self.game_size = game_size

        # game_board represent the current state of the game, 1 represent black stone, 2 represent white stone
        self.game_board = np.zeros(shape=(game_size, game_size), dtype=np.int8)
        # boardered is game_board with boarders, boarders are '3's. It has a new coordinate system which (x, y) = (x + 1, y + 1)
        self.boardered = None
        # map storing information of whether a stone have qi or not
        self.qi_map = np.zeros(shape=(game_size, game_size), dtype=np.int8)
        # group_map show which group each stone belows to
        self.group_map = np.zeros(shape=(game_size, game_size), dtype=np.int8)
        self.group_indexes = []
        # da_jie is a boolean whether there is a jie
        self.da_jie = False

        self.game_history = []
        self.player = 1  # black goes
        self.rule = rule
        if handicap:
            self.handicap = []
            self.player = 2  # white goes first when handicap

    def add_boarder(self):
        # this method give boader to the game_board matrix, which will generate the boadered map of all stones
        vertical = np.ones(shape=(1, self.game_size), dtype=np.int8).T
        self.boardered = np.column_stack((3 * vertical, self.game_board, 3 * vertical))
        horizontal = np.ones(shape=(1, self.game_size + 2))
        self.boardered = np.row_stack((3 * horizontal, self.boardered, 3 * horizontal))

    def switch_side(self):
        if self.player == 1:
            return 2
        if self.player == 2:
            return 1

    def place_stone(self, location: (int, int)):
        assert 0 <= location[0] < self.game_size
        assert 0 <= location[1] < self.game_size
        assert self.game_board[location[0]][location[1]] == 0
        copy = self.game_board.copy()
        qi_map_copy = self.qi_map.copy()
        self.game_board[location[0]][location[1]] = self.player

        if self.rule == 'wuzi':
            step_result = self.wuziqi_judge(location)
        else:
            # 所有坐标加一， 把坐标换成有边缘的
            self.add_boarder()
            last_x = location[0]
            last_y = location[1]
            self.group_all_stones()

            # 最后一子的所在组
            last_group = self.group_map[last_x][last_y]

            # self.update_qi_map()
            # print('game_board', self.game_board)
            # print('group map \n', self.group_map)
            # print('group index', self.group_indexes)

            # 更新qi_map
            self.qi_map[last_x][last_y] = self.qi(last_x, last_y)
            if last_x > 0 and self.game_board[last_x - 1][last_y] != 0:
                self.qi_map[last_x - 1][last_y] = self.qi(last_x - 1, last_y)

            if last_y > 0 and self.game_board[last_x][last_y - 1] != 0:
                self.qi_map[last_x][last_y - 1] = self.qi(last_x, last_y - 1)

            if last_x < self.game_size - 1 and self.game_board[last_x + 1][last_y] != 0:
                self.qi_map[last_x + 1][last_y] = self.qi(last_x + 1, last_y)

            if last_y < self.game_size - 1 and self.game_board[last_x][last_y + 1] != 0:
                self.qi_map[last_x][last_y + 1] = self.qi(last_x, last_y + 1)

            # 判断死活
            # print('qi map \n', self.qi_map)
            result = self.qi_map * self.group_map
            # print('result map \n', result)
            # print(self.group_indexes)

            for i in range(len(self.group_indexes)):
                if self.group_indexes[i] not in result and self.group_indexes[i] != last_group:
                    # 提子
                    # print('delete', self.group_indexes[i])
                    self.del_group(self.group_indexes[i])
                    self.group_indexes[i] = 0
                    self.add_boarder()
                    self.update_qi_map()  # 更新全盘气的情况

            # 查看是否入气
            result = self.qi_map * self.group_map
            if last_group not in result:
                self.game_board[last_x][last_y] = 0
                # print('buruqi')
                return self.game_board, 'Buruqi'  # 不入气返回原状
            else:
                step_result = False

            # 查看是否打劫
            if len(self.game_history) > 2 and np.array_equal(self.game_board,
                                                             self.game_history[len(self.game_history) - 2]):
                self.game_board = copy
                self.qi_map = qi_map_copy
                # print('dajie')
                return self.game_board, 'dajie'  # 打劫返回原状
            else:
                step_result = False

        # print('appended', self.game_board)
        game_status = self.game_board.copy()
        self.game_history.append(game_status)
        # print(self.game_history)
        self.player = self.switch_side()
        return self.game_board, step_result

    def del_group(self, group):
        mask = self.group_map - group
        mask[mask != 0] = 1
        self.game_board = self.game_board * mask

    def update_qi_map(self):
        for i in range(self.game_size):
            for j in range(self.game_size):
                if self.game_board[i][j]:
                    self.qi_map[i][j] = self.qi(i, j)
                else:
                    self.qi_map[i][j] = 0

    def group_all_stones(self):
        # assign each of the stone to a group
        self.group_indexes = []
        for i in range(self.game_size):
            for j in range(self.game_size):
                if self.game_board[i][j] == 0:
                    self.group_map[i][j] = 0
                elif self.game_board[i][j] == self.boardered[i][j+1]:
                    self.group_map[i][j] = self.group_map[i - 1][j]
                    if self.game_board[i][j] == self.boardered[i+1][j] and self.group_map[i][j] != self.group_map[i][j - 1]:
                        self.group_map[self.group_map == self.group_map[i][j - 1]] = self.group_map[i][j]
                    else:
                        pass
                elif self.game_board[i][j] == self.boardered[i+1][j]:
                    self.group_map[i][j] = self.group_map[i][j - 1]
                else:
                    index = len(self.group_indexes) + 1
                    self.group_map[i][j] = index
                    self.group_indexes.append(index)

    def qi(self, x, y):
        # 判断每个子有没有气， 有气返回1， 没气返回0
        ls = [self.boardered[x][y + 1], self.boardered[x + 1][y], self.boardered[x + 1][y + 2], self.boardered[x + 2][y + 1]]
        if all(ls):
            return 0
        else:
            return 1

    def loc_group(self, x, y):
        # locate where each group
        if self.boardered[x - 1][y] == self.player:
            return self.group_map[x][y]
        elif self.boardered[x][y - 1] == self.player:
            return self.group_map[x][y]

    def da_jie(self):
        # this method monitering if there is a jie presented
        pass

    def wuziqi_judge(self, location):
        # 判断使用五子棋规则下有没有赢
        assert self.end_game is False

        # determine if there are 5 connected stones horizontally
        horizontal = 0
        x, y = location
        i, j = x, y
        while i < self.game_size:
            if self.game_board[i][j] == self.game_board[i + 1][j]:
                horizontal += 1
                i += 1
            else:
                break
        i, j = x, y
        while i >= self.game_size:
            if self.game_board[i][j] == self.game_board[i - 1][j]:
                horizontal += 1
                i -= 1
            else:
                break

        if horizontal >= 5:
            self.end_game = True
            return True

        # determine if there are 5 connected stones vertically
        vertical = 0
        x, y = location
        i, j = x, y
        while j < self.game_size:
            if self.game_board[i][j] == self.game_board[i][j + 1]:
                vertical += 1
                j += 1
            else:
                break
        i, j = x, y
        while j >= self.game_size:
            if self.game_board[i][j] == self.game_board[i][j - 1]:
                vertical += 1
                j -= 1
            else:
                break

        if vertical >= 5:
            self.end_game = True
            return True

        # determine if there are 5 connected stones diagonally from left to right
        diagonal_left = 0
        x, y = location
        i, j = x, y
        while i < self.game_size and j < self.game_size:
            if self.game_board[i][j] == self.game_board[i + 1][j + 1]:
                diagonal_left += 1
                i += 1
                j += 1
            else:
                break
        while i >= self.game_size and j >= self.game_size:
            if self.game_board[i][j] == self.game_board[i - 1][j - 1]:
                diagonal_left += 1
                i -= 1
                j -= 1
            else:
                break

        if diagonal_left >= 5:
            self.end_game = True
            return True

        # determine if there are 5 connected stones diagonally from right to left
        diagonal_right = 0
        x, y = location
        i, j = x, y
        while i >= self.game_size and j < self.game_size:
            if self.game_board[i][j] == self.game_board[i - 1][j + 1]:
                diagonal_right += 1
                i -= 1
                j += 1
            else:
                break
        i, j = x, y
        while i < self.game_size and j >= self.game_size:
            if self.game_board[i][j] == self.game_board[i + 1][j - 1]:
                diagonal_right += 1
                i += 1
                j -= 1
            else:
                break

        if diagonal_right >= 5:
            self.end_game = True
            return 'end_game'

    def revert(self):
        # revert the game play to the last state
        self.game_board = self.game_history[len(self.game_history) - 1]
        del self.game_history[len(self.game_history)]
        self.switch_side()

    def Zhong_guo(self):
        pass
