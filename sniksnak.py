
import os
import warnings


# hide Pygame welcome
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# ignore  AVX2 runtime warning
warnings.filterwarnings("ignore", category=RuntimeWarning, message="Your system is avx2 capable")

import pygame
pygame.init()

import random as rnd
import time
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SPRITES_DIR = os.path.join(SCRIPT_DIR, "sprites")
HEAD_IMG_PATH = os.path.join(SPRITES_DIR, "head.png")
TAIL_IMG_PATH = os.path.join(SPRITES_DIR, "tail.png")
STRAIGHT_IMG_PATH = os.path.join(SPRITES_DIR, "straight.png")
CURVE_UR_IMG_PATH = os.path.join(SPRITES_DIR, "curve_ur.png")
CURVE_UL_IMG_PATH = os.path.join(SPRITES_DIR, "curve_ul.png")
FRUIT_NORMAL_IMG_PATH = os.path.join(SPRITES_DIR, "fruit_n.png")
FRUIT_UROBOR_IMG_PATH = os.path.join(SPRITES_DIR, "fruit_u.png")
FRUIT_GHOST_IMG_PATH = os.path.join(SPRITES_DIR, "fruit_g.png")

# TODO:
# score in segment displays
# uroboros bloody mouth and tail
# ghost holy circle
# use tuples
# optional wall wrapping
# setting for ability likelyhood

class Game:

    def __init__(self, cols, rows, sq_size):

        self.cols = cols
        self.rows = rows
        self.sq_size = sq_size

        self.width = cols * sq_size
        self.height = rows * sq_size

        self.screen = pygame.display.set_mode((self.width, self.height))

        # direction vector, default right
        self.direction = [1,0]
        # user controlled direction
        # gets assigned at the end of the loop
        self.next_direction = [1,0]

        self.score = 0

        self.snake = Snake((0,0), (1,0), self.rows, self.cols, self.direction)
        self.straight_img = pygame.transform.scale(
            pygame.image.load(STRAIGHT_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.head_img = pygame.transform.scale(
            pygame.image.load(HEAD_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.tail_img = pygame.transform.scale(
            pygame.image.load(TAIL_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.curve_ur_img = pygame.transform.scale(
            pygame.image.load(CURVE_UR_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.curve_ul_img = pygame.transform.scale(
            pygame.image.load(CURVE_UL_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        
        self.fruit_normal_img = pygame.transform.scale(
            pygame.image.load(FRUIT_NORMAL_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.fruit_urobor_img = pygame.transform.scale(
            pygame.image.load(FRUIT_UROBOR_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))
        self.fruit_ghost_img = pygame.transform.scale(
            pygame.image.load(FRUIT_GHOST_IMG_PATH).convert_alpha(), (self.sq_size, self.sq_size))


        self.fruit = Fruit((rnd.randrange(self.cols), rnd.randrange(self.rows)))
        self.fruit_sprite = self.fruit_normal_img
        
        self.ghost = False
        self.ghost_activated = False

        self.uroboros = False
        self.uroboros_activated = False
        

        self.clock = pygame.time.Clock()


    def draw_background(self):
        self.screen.fill((34, 139, 34))
    
    def get_snake_sprite(self, vecu, vecv):

        # vecu is None = head
        if vecu is None:
            if vecv == (0, 1): return pygame.transform.rotate(self.head_img, 90)
            elif vecv == (0, -1): return pygame.transform.rotate(self.head_img, 270)
            elif vecv == (1, 0): return pygame.transform.rotate(self.head_img, 180)
            return self.head_img

        # vecv is None = tail
        if vecv is None:
            if vecu == (0, 1): return pygame.transform.rotate(self.tail_img, 90)
            elif vecu == (0, -1): return pygame.transform.rotate(self.tail_img, 270)
            elif vecu == (1, 0): return pygame.transform.rotate(self.tail_img, 180)
            return self.tail_img
        
        # vertical straight
        if vecu[0] == 0 and vecv[0] == 0:
            # moving down
            if vecu[1] == 1:
                return pygame.transform.rotate(self.straight_img, 270)
            # moving up
            return pygame.transform.rotate(self.straight_img, 90)

        # horizontal straight
        if vecu[1] == 0 and vecv[1] == 0:
            # moving left
            if vecu[0] == 1:
                return pygame.transform.rotate(self.straight_img, 180)
            # moving right
            return self.straight_img

        # curve going
        # down and left
        if vecu == (1, 0) and vecv == (0, -1):
            return pygame.transform.rotate(self.curve_ur_img, 180)
        # right and up
        if vecu == (0, 1) and vecv == (-1, 0):
            return pygame.transform.rotate(self.curve_ul_img, 270)
        # down and right
        if vecu == (-1, 0) and vecv == (0, -1):
            return pygame.transform.rotate(self.curve_ul_img, 180)
        # left and up
        if vecu == (0, 1) and vecv == (1, 0):
            return pygame.transform.rotate(self.curve_ur_img, 90)
        # up and right
        if vecu == (-1, 0) and vecv == (0, 1):
            return self.curve_ur_img
        # up and left
        if vecu == (1, 0) and vecv == (0, 1):
            return self.curve_ul_img
        # left and down
        if vecu == (0, -1) and vecv == (1, 0):
            return pygame.transform.rotate(self.curve_ul_img, 90)
        # right and down
        if vecu == (0, -1) and vecv == (-1, 0):
            return pygame.transform.rotate(self.curve_ur_img, 270)
        
        return self.straight_img

    def draw_snake(self):
        # reversed because otherwise when ghost is active, the passing part is underneath
        for idx, segment in reversed(list(enumerate(self.snake.body))):
            vecu = None
            vecv = None
            x, y = segment
            px = x * self.sq_size
            py = y * self.sq_size

            if idx > 0:
                x_prev, y_prev = self.snake.body[idx - 1]
                vecu = (x - x_prev, y - y_prev)

            if idx < self.snake.body_len - 1:
                x_next, y_next = self.snake.body[idx + 1]
                vecv = (x_next - x, y_next - y)
            
            sprite = self.get_snake_sprite(vecu, vecv)
            

            self.screen.blit(sprite, (px, py))

    def gen_fruit_coords(self):
        x = rnd.randrange(self.cols)
        y = rnd.randrange(self.rows)

        self.fruit.pos = (x, y)

        rand_ability = rnd.randrange(100)

        if (rand_ability % 10 == 0 and not self.ghost):
            self.ghost = True
            self.fruit_sprite = self.fruit_ghost_img
        elif (rand_ability % 5 == 0 and not self.uroboros):
            self.uroboros = True
            self.fruit_sprite = self.fruit_urobor_img
        else:
            self.fruit_sprite = self.fruit_normal_img


    def check_fruit_eaten(self):
        if self.snake.body[0] == self.fruit.pos:
            self.snake.grow = True
            self.score += 1
            self.gen_fruit_coords()

    def spawn_fruit(self):
        x, y = self.fruit.pos

        px = x * self.sq_size
        py = y * self.sq_size
        
        self.screen.blit(self.fruit_sprite, (px, py))

    def check_collision(self):
        for idx, seg in enumerate(self.snake.body[1:]):
            if (seg == self.snake.body[0]):
                return idx
        
        return 0

    def event_handler(self):

        for event in pygame.event.get():

            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()

            elif (event.type == pygame.KEYDOWN):
                if (event.key == pygame.K_UP):
                    self.next_direction = [0,-1]
                elif (event.key == pygame.K_DOWN):
                    self.next_direction = [0,1]
                elif (event.key == pygame.K_LEFT):
                    self.next_direction = [-1,0]
                elif (event.key == pygame.K_RIGHT):
                    self.next_direction = [1,0]
                elif (event.key == pygame.K_e and self.ghost == True):

                    self.ability_end = time.time() + 10
                    self.ghost_activated = True
                    self.ghost = False
                
                elif (event.key== pygame.K_f and self.uroboros == True):
                    self.uroboros = False
                    self.uroboros_activated = True

        


    def set_direction(self, new_direction):
        if (self.direction != [-new_direction[0], -new_direction[1]]): # check for opposite direction
            self.direction = new_direction
            self.snake.direction = new_direction
    
    def exec_urobor(self, intersection):
        if (intersection != 0):
            self.snake.body = self.snake.body[:intersection]
            self.snake.body_len = intersection
            self.uroboros_activated = False

    def exec_ghost(self):
        if (time.time() > self.ability_end):
            self.ghost_activated = False

    def game_loop(self):

        while True:
            self.event_handler()

            self.draw_background()

            self.set_direction(self.next_direction)
            self.snake.move()

            intersection = self.check_collision()

            if (self.uroboros_activated):
                self.exec_urobor(intersection)

            elif (self.ghost_activated):
                self.exec_ghost()

            else:
                if (intersection != 0):
                    print("Game over")
                    pygame.time.wait(1000)
                    pygame.quit()
                    sys.exit()
        
                
            self.check_fruit_eaten()
            self.spawn_fruit()
            self.draw_snake()
            
            pygame.display.flip()
            self.clock.tick(8)


class Snake:
    def __init__(self, head, tail, rows, cols, direction):

        self.body = [head, tail]
        self.body_len = 2

        self.grow = False
        self.direction = direction

        # needed for wrapping inside move
        self.rows = rows
        self.cols = cols

    def move(self):
        head_x, head_y = self.body[0] # head

        new_head = ((head_x + self.direction[0]) % self.cols, 
                    (head_y + self.direction[1]) % self.cols)

        self.body = [new_head] + self.body

        if self.grow == False:
            self.body = self.body[:self.body_len]
        else:
            self.body_len += 1
            self.grow = False


class Fruit:
    def __init__(self, pos):
        self.pos = pos


COLS = 10
ROWS = 10
SQUARE_SIZE = 128

game = Game(COLS, ROWS, SQUARE_SIZE)
game.game_loop()
