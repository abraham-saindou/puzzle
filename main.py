import pygame
import random
from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, text):
        pygame.font.init()
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.x, self.y = x, y
        self.text = text
        self.rect = self.image.get_rect()
        if self.text != "empty":
            self.font = pygame.font.SysFont("Consolas", 50)
            font_surface = self.font.render(self.text, True, BLACK)
            self.image.fill(WHITE)
            self.font_size = self.font.size(self.text)
            draw_x = (TILESIZE / 2) - self.font_size[0] / 2
            draw_y = (TILESIZE / 2) - self.font_size[1] / 2
            self.image.blit(font_surface, (draw_x, draw_y))
        else:
            self.image.fill(BGCOLOR)

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def click(self, mouse_x, mouse_y):
        return self.rect.left <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.bottom

    def left(self):
        return self.rect.x - TILESIZE >= 0

    def up(self):
        return self.rect.y - TILESIZE >= 0

    def right(self):
        return self.rect.x + TILESIZE < GAMESIZE * TILESIZE

    def down(self):
        return self.rect.y + TILESIZE < GAMESIZE * TILESIZE
class UIElement:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw(self, screen):
        font = pygame.font.SysFont("Consolas", 50)
        text = font.render(self.text, True, WHITE)
        screen.blit(text, (self.x, self.y))
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.color, self.text_color = color, text_color
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.text = text

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("Consolas", 30)
        text = font.render(self.text, True, self.text_color)
        self.font_size = font.size(self.text)
        draw_x = self.x + (self.width / 2) - self.font_size[0] / 2
        draw_y = self.y + (self.height / 2) - self.font_size[1] / 2
        screen.blit(text, (draw_x, draw_y))

    def click(self, mouse_x, mouse_y):
        return self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height


class PuzzleGame(Tile, UIElement, Button):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.shuffling_timer = 0
        self.shuffling = False
        self.prechoice = ""
        self.button_list = []
        self.user_score = 0
        self.list_userscore = []

    def init_game(self):
        grid = [[x + y * GAMESIZE for x in range(1, GAMESIZE + 1)] for y in range(GAMESIZE)]
        grid[-1][-1] = 0
        return grid

    def randomizer(self):
        moves = []
        for row, tile in enumerate(self.tiles_grid):
            for col, tiles in enumerate(self.tiles_grid):
                if tile.text == "empty":
                    if tile.left():
                        moves.append("left")
                    if tile.right():
                        moves.append("right")
                    if tile.up():
                        moves.append("up")
                    if tile.down():
                        moves.append("down")
                break
            if len(moves) > 0:
                break

        if self.prechoice == "right":
            moves.remove("left") if "left" in moves else moves
        elif self.prechoice == "left":
            moves.remove("right") if "right" in moves else moves
        elif self.prechoice == "up":
            moves.remove("down") if "down" in moves else moves
        elif self.prechoice == "down":
            moves.remove("up") if "up" in moves else moves

        choice = random.choice(moves)
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], \
                                                                       self.tiles_grid[row][col]
        elif choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], \
                                                                       self.tiles_grid[row][col]
        elif choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], \
                                                                       self.tiles_grid[row][col]
        elif choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], \
                                                                       self.tiles_grid[row][col]



    def draw_tiles(self):
        self.tiles = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                else:
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.init_game()
        self.tiles_grid_complet = self.init_game()

        self.button_list.append(Button(775, 100, 200, 50, "Randomize", WHITE, BLACK))
        self.button_list.append(Button(775, 170, 200, 50, "Reset", WHITE, BLACK))
        self.draw_tiles()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()

    def draw_grid(self):
        for row in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 0), (row, GAMESIZE * TILESIZE))
        for col in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, col), (GAMESIZE * TILESIZE, col))

    def draw(self):
        if self.shuffling:
            self.shuffle()
            self.draw_tiles()
        else:
            self.screen.fill(BGCOLOR)
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            self.draw_grid()
            for button in self.button_list:
                button.draw(self.screen)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x, mouse_y):
                            if tile.right() and self.tiles_grid[row][col + 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], self.tiles_grid[row][col]
                            if tile.left() and self.tiles_grid[row][col - 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][col - 1], self.tiles_grid[row][col]

                            if tile.up() and self.tiles_grid[row - 1][col] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][col], self.tiles_grid[row][col]

                            if tile.down() and self.tiles_grid[row + 1][col] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][col], self.tiles_grid[row][col]

                            self.draw_tiles()
                for button in self.button_list:
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Random":
                            self.shuffling_timer = 0
                            self.shuffling = True
                        if button.text == "Reset":
                            self.new()
game = PuzzleGame()
if __name__ == '__main__':
    game.new()
    game.run()