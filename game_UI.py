import pygame
import time
import sys
import numpy as np
from game_engine import GoGame
from pygame.locals import *

NAME = "Go_Simulator"
background_image_filename = 'bg.png'
INIT_SCREENSIZE = (640, 480)
GAME_SIZE = 19
FILL_COLOR = (222, 156, 69)
global grid_size
global x_margin
global y_margin


def redo_grill(screen_width, screen_height, game_size):
    game_size = game_size
    global grid_size
    global x_margin
    global y_margin

    if screen_width > screen_height:
        grid_size = np.round(screen_height / (game_size + 3))
        y_margin = np.round(1.5 * grid_size)
        x_margin = (screen_width - screen_height) / 2 + y_margin
    else:
        grid_size = np.round(screen_width / (game_size + 3))
        x_margin = np.round(1.5 * grid_size)
        y_margin = (screen_height - screen_width) / 2 + x_margin

    line_width = np.int(grid_size / 20)
    # print('grid_info', grid_size, 'margin', (x_margin, y_margin))
    x = x_margin
    y = y_margin
    # 画横线
    y2 = y + (game_size - 1)*grid_size - 1
    for i in range(game_size):
        pygame.draw.line(screen, (0, 0, 0), (x, y), (x, y2), width=line_width)
        x += grid_size
        # x += line_width
    # 画竖线
    x2 = x_margin + (game_size - 1)*grid_size
    for j in range(game_size):
        pygame.draw.line(screen, (0, 0, 0), (x_margin, y), (x2, y), width=line_width)
        y += grid_size
        # y += line_width
    # 画出元位
    yuanwei_size = line_width * 2.5
    yuanwei_ls = [(3, 3), (3, 9), (3, 15), (9, 9), (9, 3), (9, 15), (15, 9), (15, 3), (15, 15)]
    for (x, y) in yuanwei_ls:
        pygame.draw.circle(screen, (0, 0, 0), (x_margin + x * grid_size, y_margin + y * grid_size), yuanwei_size)

    return grid_size


def draw_stones(game_board: np.ndarray):
    global grid_size

    stone_size = 0.45 * grid_size
    for i in range(GAME_SIZE):
        for j in range(GAME_SIZE):
            if game_board[i][j] == 1:
                pygame.draw.circle(screen, (0, 0, 0), (x_margin + i * grid_size, y_margin + j * grid_size), stone_size)
            elif game_board[i][j] == 2:
                pygame.draw.circle(screen, (255, 255, 255), (x_margin + i * grid_size, y_margin + j * grid_size), stone_size)
            else:
                pass


if __name__ == '__main__':
    pygame.init()
    screen_size = INIT_SCREENSIZE
    screen_width, screen_height = screen_size
    screen = pygame.display.set_mode(screen_size, RESIZABLE, 32)
    pygame.display.set_caption(NAME + str(screen_size))
    screen.fill(FILL_COLOR)
    redo_grill(screen_width, screen_height, GAME_SIZE)
    game1 = GoGame()

    while True:

        event = pygame.event.wait()
        if event.type == QUIT:
            sys.exit()
        if event.type == VIDEORESIZE:
            screen_size = event.size
            screen = pygame.display.set_mode(screen_size, RESIZABLE, 32)
            pygame.display.set_caption(NAME + str(event.size))
        if event.type == MOUSEBUTTONDOWN:  # 当点击鼠标时
            pos_x, pos_y = pygame.mouse.get_pos()  # 获取点击鼠标的位置坐标
            pos_x = pos_x - x_margin
            pos_y = pos_y - y_margin
            if pos_x % grid_size < (grid_size * 0.25):
                x = pos_x // grid_size
            elif pos_x % grid_size > (grid_size * 0.75):
                x = pos_x // grid_size + 1
            else:
                continue

            if pos_y % grid_size < (grid_size * 0.25):
                y = pos_y // grid_size
            elif pos_y % grid_size > (grid_size * 0.75):
                y = pos_y // grid_size + 1
            else:
                continue

            stone_loc = (int(x), int(y))
            print(stone_loc)
            game1.place_stone(stone_loc)

        screen_width, screen_height = screen_size
        # 这里需要重新填充满窗口
        # for y in range(0, screen_height, background.get_height()):
        #     for x in range(0, screen_width, background.get_width()):
        #         screen.blit(background, (x, y))
        screen.fill(FILL_COLOR)
        redo_grill(screen_width, screen_height, GAME_SIZE)
        draw_stones(game1.game_board)
        pygame.display.update()
