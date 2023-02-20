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

    def move_tiles(self, key):
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                if key == pygame.K_LEFT:
                    if tile.right() and self.tiles_grid[row][col + 1] == 0:
                        self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][col + 1], \
                        self.tiles_grid[row][col]
                        return True
                elif key == pygame.K_RIGHT:
                    if tile.left() and self.tiles_grid[row][col - 1] == 0:
                        self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][
                            col - 1], \
                            self.tiles_grid[row][col]
                        return True
                elif key == pygame.K_UP:
                    if tile.down() and self.tiles_grid[row + 1][col] == 0:
                        self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][
                            col], \
                            self.tiles_grid[row][col]
                        return True
                elif key == pygame.K_DOWN:
                    if tile.up() and self.tiles_grid[row - 1][col] == 0:
                        self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][
                            col], \
                            self.tiles_grid[row][col]
                        return True
        return False


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
        self.randomizer_timer = 0
        self.start_randomize = False
        self.start_game = False
        self.changeboard_size = False
        self.file = open('userscore.txt', 'a+')

        self.prechoice = ""
        self.button_list = []
        self.size = ["3*3", "4*4", "5*5"]

        self.moved = False
        self.movement_count = 0

    def init_game(self):
        grid, num = [], 1
        for x in range(GAMESIZE):
            grid.append([])
            for y in range(GAMESIZE):
                grid[x].append(num)
                num += 1
        grid[-1][-1] = 0
        return grid

    def randomizer(self):
        #  Create possible direction to go for the empty tile
        moves = []
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
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

#
        choice = random.choice(moves)
        self.prechoice = choice
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

        self.start_game = False
        self.button_list.append(Button(775, 100, 190, 50, "Randomize", WHITE, BLACK))
        self.button_list.append(Button(775, 170, 190, 50, "Reset", WHITE, BLACK))
        self.button_list.append(Button(760, 240, 60, 50, "3*3", WHITE, BLACK))
        self.button_list.append(Button(840, 240, 60, 50, "4*4", WHITE, BLACK))
        self.button_list.append(Button(920, 240, 60, 50, "5*5", WHITE, BLACK))
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

    def layout(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.update()
        self.all_sprites.draw(self.screen)
        self.draw_grid()
        for button in self.button_list:
            button.draw(self.screen)
            self.str_movement_count = str(self.movement_count)
            UIElement(825, 35, self.str_movement_count + " moves").draw(self.screen)
            score = self.file.read()
            print(score)
            UIElement(710, 380, ("Best Score : " + score)).draw(self.screen)

    def draw(self):
        self.layout()
        if self.changeboard_size is True:
            self.new()
            print(self.tiles_grid)
            print(self.tiles)
            self.changeboard_size = False
            self.str_movement_count = ""
            self.start_game = True

        if self.start_game:
            if self.tiles_grid == self.tiles_grid_complet:
                self.start_game = False
                self.file.write("{}\n".format(self.str_movement_count + " moves"))

                print("You won by using " + self.str_movement_count + " moves")

        if self.start_randomize:
            self.randomizer()
            self.draw_tiles()
            self.randomizer_timer += 1
            if self.randomizer_timer > 80:
                self.start_randomize = False
                self.start_game = True
                self.movement_count = 0
        pygame.display.flip()

    def events(self):
        global GAMESIZE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Allows user to quit game
                pygame.quit()
                quit(0)
            if event.type == pygame.KEYDOWN:  # User press a key arrow and empty tile is moved, by using move_tiles()
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    self.moved = self.move_tiles(event.key)
                    if self.moved:
                        self.draw_tiles()
                        self.movement_count += 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x, mouse_y):
                            if tile.right() and self.tiles_grid[row][col + 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = self.tiles_grid[row][
                                    col + 1], self.tiles_grid[row][col]
                                self.movement_count += 1
                            if tile.left() and self.tiles_grid[row][col - 1] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = self.tiles_grid[row][
                                    col - 1], self.tiles_grid[row][col]
                                self.movement_count += 1
                            if tile.up() and self.tiles_grid[row - 1][col] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = self.tiles_grid[row - 1][
                                    col], self.tiles_grid[row][col]
                                self.movement_count += 1
                            if tile.down() and self.tiles_grid[row + 1][col] == 0:
                                self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = self.tiles_grid[row + 1][
                                    col], self.tiles_grid[row][col]
                                self.movement_count += 1
                    self.draw_tiles()
                for button in self.button_list:
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Randomize":
                            self.randomizer_timer = 0
                            self.start_randomize = True
                        if button.text == "Reset":
                            self.new()
                        if button.text == self.size[0]:
                            GAMESIZE = 3
                            self.changeboard_size = True
                        if button.text == self.size[1]:
                            GAMESIZE = 4
                            self.changeboard_size = True
                        if button.text == self.size[2]:
                            GAMESIZE = 5
                            self.changeboard_size = True


game = PuzzleGame()
if __name__ == '__main__':
    game.new()
    game.run()
