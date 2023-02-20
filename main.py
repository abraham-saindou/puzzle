import pygame
import random
import os
from settings import *


# Tile class is dedicated to create tiles
class Tile(pygame.sprite.Sprite):  # import sprites as pygame class in its parameter
    def __init__(self, game, x, y, text):
        pygame.font.init()  # import fonts
        self.groups = game.sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))  # Create tile surface
        self.x, self.y = x, y
        self.text = text  # Take a number converted into a str
        self.rect = self.image.get_rect()
        if self.text != "empty":
            self.font = pygame.font.SysFont("Georgia", 50)  # Choose a font and its size
            font_surface = self.font.render(self.text, True, BLACK)  # Apply font on text
            self.image.fill(MAGENTA)  # Color tile surface
            self.font_size = self.font.size(self.text)
            draw_x = (TILESIZE / 2) - self.font_size[0] / 2
            draw_y = (TILESIZE / 2) - self.font_size[1] / 2
            self.image.blit(font_surface, (draw_x, draw_y))
        else:
            self.image.fill(BLACK)  # Empty tile has a different color

    def update(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE

    def click(self, mouse_x, mouse_y):  # Function which read mouse position on a tile
        return self.rect.left <= mouse_x <= self.rect.right and self.rect.top <= mouse_y <= self.rect.bottom

    # Direction will be used to check if an empty tile can be moved with mouse or arrows
    def left(self):
        return self.rect.x - TILESIZE >= 0

    def up(self):
        return self.rect.y - TILESIZE >= 0

    def right(self):
        return self.rect.x + TILESIZE < GAMESIZE * TILESIZE

    def down(self):
        return self.rect.y + TILESIZE < GAMESIZE * TILESIZE

    # Function which binds arrows keys to the game
    def move_tiles(self, key):
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                # Check if empty tile can be moved to a direction, then invert empty tile with a tile
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


class GraphicText:  # Will display text next to the puzzle
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text

    def draw(self, screen):
        font = pygame.font.SysFont("Georgia", 30)
        text = font.render(self.text, True, WHITE)
        screen.blit(text, (self.x, self.y))


class Button:  # Class making buttons
    def __init__(self, x, y, width, height, text, color, text_color):  # Parameters
        self.color, self.text_color = color, text_color
        self.width, self.height = width, height
        self.x, self.y = x, y
        self.text = text

    def draw(self, screen):  # Uses pygame rect, font and blit functions to draw buttons
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        font = pygame.font.SysFont("Georgia", 30)
        text = font.render(self.text, True, self.text_color)
        self.font_size = font.size(self.text)
        draw_x = self.x + (self.width / 2) - self.font_size[0] / 2
        draw_y = self.y + (self.height / 2) - self.font_size[1] / 2
        screen.blit(text, (draw_x, draw_y))

    def click(self, mouse_x, mouse_y):  # Function which read mouse position on a tile
        return self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height


class PuzzleGame(Tile, GraphicText, Button):
    def __init__(self):
        pygame.init()
        # Basic parameters
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.button_list = []
        self.num = 0
        # Parameters for randomize option
        self.prechoice = ""
        self.randomizer_timer = 0
        self.start_randomize = False

        # Parameters for win condition and to change board size
        self.start_game = False
        self.finished = False
        self.changeboard_size = False
        self.size = ["3*3", "4*4", "5*5"]

        # Use for arrow binding and to count time empty tile was displaced
        self.moved = False
        self.movement_count = 0

    def init_game(self):  # Function used to create tiles_grid, it appends a number in grid
        grid, num = [], 1
        for x in range(GAMESIZE):
            grid.append([])
            for y in range(GAMESIZE):
                grid[x].append(num)
                num += 1
        grid[-1][-1] = 0
        return grid

    def randomizer(self):  #  Create possible direction to go for the empty tile
        #  Detect if empty tile can be moved and add directions to list
        moves = []
        for row, tiles in enumerate(self.tiles):  # Append moves
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
                break  # Quit the loops when moves are appended to moves list

        # Remove a choice that has been used
        if self.prechoice == "right":
            moves.remove("left") if "left" in moves else moves
        elif self.prechoice == "left":
            moves.remove("right") if "right" in moves else moves
        elif self.prechoice == "up":
            moves.remove("down") if "down" in moves else moves
        elif self.prechoice == "down":
            moves.remove("up") if "up" in moves else moves

        #  Choose a direction in moves list, invert tiles then remove it from the list
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
        # Uses tiles.grid, made by init-game(), in a nested loop to create tiles by invoking the Tile Class.
        self.tiles = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    self.tiles[row].append(Tile(self, col, row, str(tile)))
                else:
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def new(self):
        self.sprites = pygame.sprite.Group()
        self.tiles_grid = self.init_game()
        self.ordered_tiles = self.init_game()

        self.start_game = False
        self.button_list.append(Button(655, 170, 190, 50, "Randomize", BEIGE, BLACK))
        self.button_list.append(Button(640, 240, 60, 50, "3*3", BEIGE, BLACK))
        self.button_list.append(Button(720, 240, 60, 50, "4*4", BEIGE, BLACK))
        self.button_list.append(Button(800, 240, 60, 50, "5*5", BEIGE, BLACK))
        self.draw_tiles()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.draw()

    def draw_grid(self):  # Draw a grid by using draw.line()
        for row in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (row, 0), (row, GAMESIZE * TILESIZE))
        for col in range(-1, GAMESIZE * TILESIZE, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, col), (GAMESIZE * TILESIZE, col))

    def layout(self):
        self.screen.fill(BGCOLOR)
        self.sprites.update()
        self.sprites.draw(self.screen)
        self.draw_grid()
        for button in self.button_list:
            self.str_movement_count = str(self.movement_count)
            button.draw(self.screen)
            GraphicText(695, 80, self.str_movement_count + " moves").draw(self.screen)
            numint = int(self.num)
            numint2 = int(self.str_movement_count)
            best = min(numint, numint2)  # Find the smallest int, which will be displayed if file is not empty.
            if not os.path.getsize("userscore.txt"):
                GraphicText(610, 380, ("Best Score : " + self.str_movement_count)).draw(self.screen)
            else:
                GraphicText(630, 380, ("Best Score : " + str(best))).draw(self.screen)
            if self.finished is True:
                GraphicText(630, 430, "You won with " + self.str_movement_count + " moves").draw(self.screen)

    def draw(self):
        self.layout()
        # Change board size by using new()
        if self.changeboard_size is True:
            self.new()
            self.changeboard_size = False
            self.str_movement_count = ""

        # Check if the puzzle is resolved, then write result in a file if it's better than previous one
        if self.start_game:
            if self.tiles_grid == self.ordered_tiles:
                self.finished = True
                self.start_game = False
                with open('userscore.txt', 'r+') as self.file:
                    try:
                        self.best_score = self.file.readline()
                        self.num, self.text = self.best_score.split()
                    except:
                        if not os.path.getsize("userscore.txt") or int(self.str_movement_count) < int(self.num):
                            self.file.seek(0, 0)
                            self.file.write(str(self.str_movement_count) + " moves")
        if self.start_randomize:  # When randomize is true is start randomizer() which shuffle tiles during 80 seconds.
            self.randomizer()
            self.draw_tiles()
            self.randomizer_timer += 1
            if self.randomizer_timer > 80:
                self.start_randomize = False
                self.start_game = True
                self.movement_count = 0
        pygame.display.flip()

    def events(self):
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

            # Get mouse position, and exchange the clicked tile with the empty one
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

                global GAMESIZE  # import this variable so that user can modify grid size when press tile size buttons
                for button in self.button_list:  # Check if a button is clicked, then activate booleans
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Randomize":
                            self.randomizer_timer = 0
                            self.start_randomize = True

                        # Change board size parameters
                        if button.text == self.size[0]:
                            GAMESIZE = 3
                            self.changeboard_size = True
                        if button.text == self.size[1]:
                            GAMESIZE = 4
                            self.changeboard_size = True
                        if button.text == self.size[2]:
                            GAMESIZE = 5
                            self.changeboard_size = True


# Create an object PuzzleGame class, which uses new and run functions
game = PuzzleGame()
if __name__ == '__main__':
    game.new()
    game.run()
