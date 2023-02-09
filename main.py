import pygame
import random
import time
from settings import *


class PuzzleGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()

        self.user_score = 0
        self.list_userscore = []

    def init_game(self):
        grid = []
        num = 1
        for x in range(GAMESIZE):
            grid.append([])
            for y in range(GAMESIZE):
                grid[x].append(num)
                num += 1
        grid[-1][-1] = 0
        print(grid)
        return grid

    def create_puzzle(self):
        # GAMESIZE = int(input())
        for row in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 0), (row, GAMESIZE * TILESIZE))
        for col in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, col), (GAMESIZE * TILESIZE, col))

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.see()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)


if __name__ == '__main__':
    game = PuzzleGame()
    game.run()


