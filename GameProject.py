# importing libraries
import pygame
import NEAT
from pygame._freetype import STYLE_DEFAULT
from pygame.locals import *
import sys
import random
import math
import pygame.freetype

pygame.freetype.init()
pygame.font.init()

endState = 0
level_num = 1
menu_option = True
time = 0
text_time = 0
pause_menu = False

# assigning constants
# set fps
FPS = 30
framePerSec = pygame.time.Clock()

# set frame
WIDTH = 450
HEIGHT = 400

# color
BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 255)
LIGHT_BLUE = pygame.Color(40, 175, 255)
GREEN = pygame.Color(0, 255, 0)
GREY = pygame.Color(90, 90, 90)
LIGHT_GREY = pygame.Color(170, 170, 170)
RED = pygame.Color(255, 0, 0)
WHITE = pygame.Color(255, 255, 255)

# distances
END_FLAG_LOCATION = ((WIDTH * 11) / 30, (HEIGHT * 7) / 20)
PLATFORM_1_LOCATION = (WIDTH / 6, (HEIGHT * 5) / 6)
PLATFORM_2_LOCATION = (WIDTH / 2, (2 * HEIGHT) / 3)
PLATFORM_3_LOCATION = ((7 * WIDTH) / 12, HEIGHT / 2)
PLATFORM_4_LOCATION = (WIDTH / 3, (HEIGHT * 5) / 12)

SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))

# Fonts
FONT_TIMER = pygame.font.SysFont('arial', 16)
FONT_WIN_LOSE = pygame.font.SysFont('arial', 22)
FONT_TITLE = pygame.freetype.SysFont('arial', 22)

#organism count
ORG_POPULATION = 150
ORG_MUTATION = 0.5 #Max proportion of the population to mutate
'''
The ground for the game, unique sprite
outputs: a sprite object that needs to be created and added to the sprites group
'''

class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([WIDTH, HEIGHT - (HEIGHT - 10)])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT - 5))
        self.x = self.rect.x
        self.y = self.rect.y

'''
The platforms throughout the level
inputs: xLoc = the left most location, yLoc = the top most location, width = the length of the platform
outputs: a sprite object that needs to be created and added to the sprites group
'''
class Platform(pygame.sprite.Sprite):
    def __init__(self, x_loc, y_loc, width):
        super().__init__()
        self.x = x_loc
        self.y = y_loc
        self.image = pygame.Surface((width, HEIGHT / 30))
        self.image.fill(LIGHT_GREY)
        pygame.draw.rect(self.image, LIGHT_GREY, pygame.Rect(x_loc, y_loc, width, HEIGHT / 30))
        self.rect = self.image.get_rect(left=x_loc, top=y_loc, )

'''  
The Flag pole for the start and end flags
inputs: xLoc = the left most location, yLoc = the top most location
outputs: a sprite object that needs to be created and added to the sprites group
'''
class FlagPole(pygame.sprite.Sprite):
    def __init__(self, x_loc, y_loc):
        super().__init__()
        self.image = pygame.Surface((WIDTH / 5, 1))
        self.image.fill(GREY)
        pygame.draw.rect(self.image, BLACK, pygame.Rect(x_loc, y_loc, WIDTH / 60, HEIGHT / 60))
        self.rect = self.image.get_rect(left=x_loc, top=y_loc)

    # Triggers a type of ending
    def update(self):
        hit_enemy = pygame.sprite.spritecollide(self, enemies, True)
        hit_player = pygame.sprite.spritecollide(self, players, True)
        global text_time
        global endState
        if hit_enemy and endState == 0:
            endState = -1
            text_time = pygame.time.get_ticks()
        if hit_player and endState == 0:
            endState = 1
            text_time = pygame.time.get_ticks()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.w = 10
        self.rect.h = 10
        self.inputs = [False, False, False]
        self.vy = 0
        self.jump = False

    def update(self):
        dx = 0
        dy = 0

        # input
        self.inputs = self.get_input()
        if self.inputs[0]:
            dx -= 5
        if self.inputs[1]:
            dx += 5
        if self.inputs[2]:
            if self.jump:
                self.vy = -10

        # gravity
        dy += self.vy
        self.vy = min(self.vy + 1, 10)

        # initial movements
        self.rect.x += dx
        self.rect.y += dy

        # constraints
        self.rect = self.rect.clamp(0, 0, WIDTH, HEIGHT)
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.rect.y = hits[0].rect.top - self.rect.h
            self.vy = 0
            self.jump = True
        else:
            self.jump = False

    # Each enemy should have their own version of this, with an algorithm telling it what "keys" to press each frame.
    # Index 0 is left; 1, right; 2, jump.
    def get_input(self):
        key = pygame.key.get_pressed()
        return [key[pygame.K_LEFT], key[pygame.K_RIGHT], key[pygame.K_UP]]

class Enemy(Player):
    def __init__(self, x, y, org):
        super().__init__(x, y)
        self.image.fill((random.randrange(0, 256), random.randrange(0, 256), random.randrange(0,256), 192));
        self.organism = org;
        self.outputs = [];
        self.choice = -1;
        self.closest = 99999; #The closest this enemy ever gets to the flag. Using this instead of immediate distance, as the player could manipulate that to quash certain organisms.

    # It is repeated in order to add in the two functions, (get_closest_higher_platform() and get_distance_flag())
    def update(self):
        super().update()
        # flag collision, records time
        hit_flag = pygame.sprite.spritecollide(self, endPoint, False)
        if hit_flag:
            global time
            entity_time = time/30
            self.organism.fitness = self.fitness(entity_time)

    def get_input(self):
        self.outputs = self.organism.forward_prop(tuple((
            NEAT.sigmoid(self.get_closest_higher_platform_distance()), 
            NEAT.sigmoid(self.get_distance_flag()), 
            NEAT.sigmoid(self.get_closest_higher_platform_distance_x()), 
            NEAT.sigmoid(self.get_closest_higher_platform_distance_y()))))
        self.choice = self.outputs.index(max(self.outputs))
        return [self.choice in range(2), self.choice in range(3,5), self.choice in range(1, 4)];
    
    '''
    gets the distance between the the current agent and the flag pole
    '''
    def get_distance_flag(self):
        localOut = get_distance(END_FLAG_LOCATION[0] - self.rect.x, END_FLAG_LOCATION[1] - self.rect.y)
        self.closest = min(self.closest, localOut)
        return localOut

    '''    
    gets the closest platform that is higher than the current agent
    if the highest platform is lower than the agent then it return None 
    Note: lower y value means it is higher in the screen
    '''
    def get_closest_higher_platform(self):
        if self.rect.y < platform4.y:
            return None
        platform_pointer_distance = get_distance(ground.x - self.rect.x, ground.y - self.rect.y)
        platform_pointer = ground
        for platform_current in platforms:
            current_distance = get_distance(platform_current.rect.centerx - self.rect.x, platform_current.rect.centery - self.rect.y)
            if platform_pointer_distance > current_distance and self.rect.y > platform_current.rect.centery:
                platform_pointer = platform_current
                platform_pointer_distance = current_distance
        return platform_pointer

    '''
    gets the closest platform distance that is higher than the current agent
    if the highest platform is lower than the agent then it return -1 
    '''
    def get_closest_higher_platform_distance(self):
        platform = self.get_closest_higher_platform()
        return 0 if platform is None else get_distance(platform.rect.centerx-self.rect.x, platform.rect.centery - self.rect.y) 
        '''
        current_distance = 0
        if platform_pointer is None:
            current_distance = -1
        else:
            current_distance = get_distance(platform_pointer.rect.centerx - self.rect.x, platform_pointer.rect.centery - self.rect.y)
        return current_distance'''

    '''
    gets the x value that is needed to get the center of the closest platform
    positive value means that the agent is to the left of the center of the closest platform
    if the highest platform is lower than the agent then it return 0 
    '''
    def get_closest_higher_platform_distance_x(self):
        platform_pointer = self.get_closest_higher_platform()
        current_distance_x = 0
        if platform_pointer is None:
            current_distance_x = 0;
        else:
            current_distance_x = platform_pointer.rect.centerx - self.rect.x
        return current_distance_x

    '''
    gets the closest platform y value of distance that is higher than the current agent
    lower numbers mean that it is closer to the center of the closest platform
    if the highest platform is lower than the agent then it return -1 
    '''
    def get_closest_higher_platform_distance_y(self):
        platform_pointer = self.get_closest_higher_platform()
        if platform_pointer is None:
            current_distance_y = 0
        else:
            current_distance_y = self.rect.y - platform_pointer.rect.centery
        return current_distance_y

    # gets the fitness for the enemy
    def fitness(self, entity_time):
        constant1 = 5
        constant2 = 10
        return constant1/(1 + self.closest) #+ constant2/(1 + entity_time)


# update background
def update_bg():
    SURFACE.fill(LIGHT_BLUE)

    # drawing mountain background
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH / 2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH / 3), int(HEIGHT / 3)), (int(WIDTH / 2), 0),
                                         (int(WIDTH * (2 / 3)), int(HEIGHT / 3))])

    # start flag, remains static
    pygame.draw.polygon(SURFACE, RED, [((2 * WIDTH) / 25, (14 * HEIGHT) / 15), ((17 * WIDTH) / 300, (14 * HEIGHT) / 15),
                                       ((2 * WIDTH) / 25, (9 * HEIGHT) / 10)])
    pygame.draw.line(SURFACE, BLACK, (WIDTH / 12, HEIGHT), (WIDTH / 12, (9 * HEIGHT) / 10), (int)(WIDTH / 100))

def update_pause():
    # background
    SURFACE.fill(LIGHT_BLUE)
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH / 2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH / 3), int(HEIGHT / 3)), (int(WIDTH / 2), 0),
                                         (int(WIDTH * (2 / 3)), int(HEIGHT / 3))])
    pygame.draw.line(SURFACE, GREEN, (0, HEIGHT - 5), (WIDTH, HEIGHT - 5), 10)

    # buttons
    pygame.draw.ellipse(SURFACE, WHITE, ((WIDTH / 3, (2 * HEIGHT) / 5), (WIDTH / 3, HEIGHT / 11)))
    pygame.draw.ellipse(SURFACE, WHITE, ((WIDTH / 3, (3 * HEIGHT) / 5), (WIDTH / 3, HEIGHT / 11)))

    start_text = FONT_TIMER.render("Resume Game", True, BLACK)
    SURFACE.blit(start_text, ((19 * WIDTH) / 45, (17 * HEIGHT) / 40))
    quit_text = FONT_TIMER.render("Quit Game", True, BLACK)
    SURFACE.blit(quit_text, ((19 * WIDTH) / 45, (5 * HEIGHT) / 8))
    FONT_TITLE.render_to(SURFACE, (WIDTH / 8, HEIGHT / 2), "Pause", BLACK, None, STYLE_DEFAULT,61, 0)

def update_bg_menu():
    # background
    SURFACE.fill(LIGHT_BLUE)
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH / 2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH / 3), int(HEIGHT / 3)), (int(WIDTH / 2), 0),
                                         (int(WIDTH * (2 / 3)), int(HEIGHT / 3))])
    pygame.draw.line(SURFACE, GREEN, (0, HEIGHT - 5), (WIDTH, HEIGHT - 5), 10)

    # buttons
    pygame.draw.ellipse(SURFACE, WHITE, ((WIDTH / 3, (2 * HEIGHT) / 5), (WIDTH / 3, HEIGHT / 11)))
    pygame.draw.ellipse(SURFACE, WHITE, ((WIDTH / 3, (3 * HEIGHT) / 5), (WIDTH / 3, HEIGHT / 11)))

    # text
    start_text = FONT_TIMER.render("Start Game", True, BLACK)
    SURFACE.blit(start_text, ((19 * WIDTH) / 45, (17 * HEIGHT) / 40))
    quit_text = FONT_TIMER.render("Quit Game", True, BLACK)
    SURFACE.blit(quit_text, ((19 * WIDTH) / 45, (5 * HEIGHT) / 8))
    FONT_TITLE.render_to(SURFACE, (WIDTH / 16, HEIGHT / 4), "Race Up Stair-Case Mountain", BLACK, None, STYLE_DEFAULT,
                         61, 0)

#One enemy is created for each organism.
def generate_enemies():
    for i in range(len(allOrganisms)): 
        enmTemp = Enemy(WIDTH/12, HEIGHT, allOrganisms[i])
        allSprites.add(enmTemp)
        enemies.add(enmTemp) 

# removes all of the current playing entities and spawns them back at the startflag
# also updates the network
def resetPlayers(orgList):
    global player
    global endState
    endState = 0;
    for entity in enemies:
        entity.organism.fitness = entity.fitness(30)
        entity.kill()
    player.kill()

    player = Player(WIDTH / 12, HEIGHT)
    players.add(player)
    allSprites.add(player)
    orgList = NEAT.Selection.selection(orgList, ORG_POPULATION)
    NEAT.Mutation.mutate_gen(orgList, ORG_MUTATION)
    generate_enemies()

# gets the distance
def get_distance(x, y):
    return int(math.sqrt((x ** 2) + (y ** 2)))

#prints the time of the timer
def timer():
    timer_text = FONT_TIMER.render("Time %.2f" % (time / 30), True, BLACK)
    SURFACE.blit(timer_text, (0, 0))

# prints the level
def level():
    level_text = FONT_TIMER.render("level %d" % level_num, True, BLACK)
    SURFACE.blit(level_text, (WIDTH - (WIDTH / 9), 0))

# initializing the pygame
pygame.init()
pygame.display.set_caption('The Race Up Stair-Case Mountain')

ground = Ground()
player = Player(WIDTH / 12, HEIGHT)

#Creating a group of organisms

allOrganisms = []
for i in range(ORG_POPULATION):
    orgTemp = NEAT.Organism(4,5)
    for j in range(4):
        for k in range(4, 9):
            orgTemp.add_edge(j, k, 0.5) #Starting with random seed values. Jus' to see if something different happens.
    allOrganisms.append(orgTemp)

# platform numbers go from the top so the platform that has the end flag is the highest number
platform1 = Platform(WIDTH / 6, (HEIGHT * 5) / 6, WIDTH / 3)
platform2 = Platform(WIDTH / 2, (2 * HEIGHT) / 3, WIDTH / 4)
platform3 = Platform((7 * WIDTH) / 12, HEIGHT / 2, WIDTH / 8)
platform4 = Platform(WIDTH / 3, (HEIGHT * 5) / 12, WIDTH / 5)
endFlag = FlagPole((WIDTH * 10) / 30, (HEIGHT * 9) / 22)

# to update all the sprites
allSprites = pygame.sprite.Group()
# for platform collision
platforms = pygame.sprite.Group()
# for flag collision
endPoint = pygame.sprite.Group()
players = pygame.sprite.Group()
enemies = pygame.sprite.Group()
allSprites.add(ground)
allSprites.add(player)
generate_enemies()
allSprites.add(platform1)
allSprites.add(platform2)
allSprites.add(platform3)
allSprites.add(platform4)
allSprites.add(endFlag)
platforms.add(ground)
platforms.add(platform1)
platforms.add(platform2)
platforms.add(platform3)
platforms.add(platform4)
endPoint.add(endFlag)
players.add(player)

# game running
while True:
    # menu
    while menu_option is True:
        update_bg_menu()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH / 3 <= mouse[0] <= (WIDTH * 2) / 3 and (2 * HEIGHT) / 5 <= mouse[1] <= (27 * HEIGHT) / 55:
                    menu_option = False
                if WIDTH / 3 <= mouse[0] <= (WIDTH * 2) / 3 and (3 * HEIGHT) / 5 <= mouse[1] <= (38 * HEIGHT) / 55:
                    pygame.quit()
                    sys.exit(0)
        mouse = pygame.mouse.get_pos()
        pygame.display.update()
        framePerSec.tick(FPS)
    # start of game
    update_bg()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                pause_menu = True
    # pause menu
    if pause_menu:
        while pause_menu:
            mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if WIDTH / 3 <= mouse[0] <= (WIDTH * 2) / 3 and (2 * HEIGHT) / 5 <= mouse[1] <= (27 * HEIGHT) / 55:
                        pause_menu = False
                    if WIDTH / 3 <= mouse[0] <= (WIDTH * 2) / 3 and (3 * HEIGHT) / 5 <= mouse[1] <= (38 * HEIGHT) / 55:
                        pygame.quit()
                        sys.exit(0)
            update_pause()
            pygame.display.update()
            framePerSec.tick(FPS)
# for end of level
    if endState == 1:
        winText = FONT_WIN_LOSE.render("YOU WIN", True, (0, 0, 0))
        SURFACE.blit(winText, (HEIGHT / 2, WIDTH / 2))
        if (pygame.time.get_ticks() - text_time) > 3000:
            endState = 0
            time = 0
            level_num = level_num + 1
            resetPlayers(allOrganisms)

    elif endState == -1:
        loseText = FONT_WIN_LOSE.render("YOU LOSE", True, (0, 0, 0))
        SURFACE.blit(loseText, (HEIGHT / 2, WIDTH / 2))
        if (pygame.time.get_ticks() - text_time) > 3000:
            endState = 0
            time = 0
            pygame.quit()
            sys.exit(0)
    # for timer
    time = time + 1
    timer()
    level()

    # updating the textures
    allSprites.update()
    allSprites.draw(SURFACE)
    pygame.display.update()
    # tick frame
    framePerSec.tick(FPS)