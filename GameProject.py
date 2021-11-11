# importing libraries
import pygame
import NEAT
from pygame.locals import *
import sys
import random
import math

pygame.font.init()
endState = 0
text_time = 0
level_num = 1

# assigning constants
# set fps
FPS = 30
framePerSec = pygame.time.Clock()
time = 0

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
    def __init__(self, xLoc, yLoc, width):
        super().__init__()
        self.x = xLoc
        self.y = yLoc
        self.image = pygame.Surface((width, HEIGHT / 30))
        self.image.fill(LIGHT_GREY)
        pygame.draw.rect(self.image, LIGHT_GREY, pygame.Rect(xLoc, yLoc, width, HEIGHT / 30))
        self.rect = self.image.get_rect(left=xLoc, top=yLoc, )


'''  
The Flag pole for the start and end flags
inputs: xLoc = the left most location, yLoc = the top most location
outputs: a sprite object that needs to be created and added to the sprites group
'''

class FlagPole(pygame.sprite.Sprite):
    def __init__(self, xLoc, yLoc):
        super().__init__()
        self.image = pygame.Surface((WIDTH / 100, (2 * HEIGHT) / 25))
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, BLACK, pygame.Rect(xLoc, yLoc, WIDTH / 100, HEIGHT / 60))
        self.rect = self.image.get_rect(left=xLoc, top=yLoc)

    # Triggers a type of ending
    def update(self):
        hitEnemy = pygame.sprite.spritecollide(self, enemies, True)
        hitPlayer = pygame.sprite.spritecollide(self, players, True)
        global text_time
        global endState
        if hitEnemy:
            endState = -1
            text_time = pygame.time.get_ticks()
        if hitPlayer:
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
        dx = 0;
        dy = 0;

        # input
        self.inputs = self.get_input()
        if self.inputs[0]:
            dx -= 5
        if self.inputs[1]:
            dx += 5
        if self.inputs[2]:
            if (self.jump):
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
            self.vy = 0;
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

    #It is repeated in order to add in the two functions, (get_closest_higher_platform() and get_distance_flag())
    def update(self):
        super()
        dx = 0;
        dy = 0;
        self.inputs = self.get_input()
        if self.inputs[0]:
            dx -= 5
        if self.inputs[1]:
            dx += 5
        if self.inputs[2]:
            if (self.jump):
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
            self.vy = 0;
            self.jump = True
        else:
            self.jump = False

    def get_input(self):
        self.outputs = self.organism.forward_prop(tuple((
            self.get_closest_higher_platform_distance(), 
            self.get_distance_flag(), 
            self.get_closest_higher_platform_distance_x(), 
            self.get_closest_higher_platform_distance_y())))
        print(self.outputs)
        self.choice = self.outputs.index(max(self.outputs))
        return [self.choice in range(2), self.choice in range(3,5), self.choice in range(1, 4)]; 
        
    '''
    gets the distance between the the current agent and the flag pole
    '''    
    def get_distance_flag(self):
        return get_distance(END_FLAG_LOCATION[0] - self.rect.x, END_FLAG_LOCATION[1] - self.rect.y)
    
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
        platform_pointer = self.get_closest_higher_platform()
        current_distance = 0
        if platform_pointer is None:
            current_distance = -1
        else:
            current_distance = get_distance(platform_pointer.rect.centerx - self.rect.x, platform_pointer.rect.centery - self.rect.y)
        return current_distance

    '''
    gets the x value that is needed to get the center of the closest platform
    positive value means that the agent is to the left of the center of the closest platform
    if the highest platform is lower than the agent then it return -99999 
    '''

    def get_closest_higher_platform_distance_x(self):
        platform_pointer = self.get_closest_higher_platform()
        current_distance_x = 0
        if platform_pointer is None:
            current_distance_x = -99999
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
        current_distance_y = 0
        if platform_pointer is None:
            current_distance_y = -1
        else:
            current_distance_y = self.rect.y - platform_pointer.rect.centery
        return current_distance_y

# update background
def update_bg():
    SURFACE.fill(LIGHT_BLUE)

    # drawing mountain background
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH / 2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH / 3), int(HEIGHT / 3)), (int(WIDTH / 2), 0),
                                         (int(WIDTH * (2 / 3)), int(HEIGHT / 3))])

    # end flag, remains static
    pygame.draw.polygon(SURFACE, RED, [((11 * WIDTH) / 30, (23 * HEIGHT) / 60), ((17 * WIDTH) / 50, (23 * HEIGHT / 60)),
                                       ((11 * WIDTH) / 30, (7 * HEIGHT) / 20)])

    # start flag, remains static
    pygame.draw.polygon(SURFACE, RED, [((2 * WIDTH) / 25, (14 * HEIGHT) / 15), ((17 * WIDTH) / 300, (14 * HEIGHT) / 15),
                                       ((2 * WIDTH) / 25, (9 * HEIGHT) / 10)])
    pygame.draw.line(SURFACE, BLACK, (WIDTH / 12, HEIGHT), (WIDTH / 12, (9 * HEIGHT) / 10), (int)(WIDTH / 100))


# removes all of the current playing entities and spawns them back at the startflag
def resetPlayers():
    global player
    for entity in enemies:
        entity.kill()
    player.kill()
    player = Player(WIDTH / 12, HEIGHT)
    players.add(player)
    allSprites.add(player)
    enemy = Enemy(WIDTH / 12, HEIGHT, RED)
    enemies.add(enemy)
    allSprites.add(enemy)


# gets the distance
def get_distance(x, y):
    return int(math.sqrt((x ** 2) + (y ** 2)))

# prints the time of the timer
def timer(time_num):
    timer_text = FONT_TIMER.render("Time %.2f" % (time / 30), True, BLACK)
    SURFACE.blit(timer_text, (0, 0))


# prints the level
def level(level_num):
    level_text = FONT_TIMER.render("level %d" % level_num, True, BLACK)
    SURFACE.blit(level_text, (WIDTH - (WIDTH / 12), 0))


# initializing the pygame
pygame.init()
pygame.display.set_caption('The Race Up Stair-Case Mountain')

ground = Ground()
player = Player(WIDTH / 2, HEIGHT / 2)

#Creating a group of organisms

allOrganisms = []; 
for i in range(1):
    orgTemp = NEAT.Organism(4,5)
    for j in range(4):
        for k in range(4, 9):
            orgTemp.add_edge(j, k, random.random()) #Starting with random seed values. Jus' to see if something different happens.
    allOrganisms.append(orgTemp)
# platform numbers go from the top so the platform that has the end flag is the highest number
platform1 = Platform(WIDTH / 6, (HEIGHT * 5) / 6, WIDTH / 3)
platform2 = Platform(WIDTH / 2, (2 * HEIGHT) / 3, WIDTH / 4)
platform3 = Platform((7 * WIDTH) / 12, HEIGHT / 2, WIDTH / 8)
platform4 = Platform(WIDTH / 3, (HEIGHT * 5) / 12, WIDTH / 5)
endFlag = FlagPole((WIDTH * 11) / 30, (HEIGHT * 7) / 20)



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

for i in range(len(allOrganisms)): #One enemy is created for each organism.
    enmTemp = Enemy(WIDTH/2, HEIGHT/2, allOrganisms[i])
    allSprites.add(enmTemp)
    enemies.add(enmTemp) 
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
    # pygame.display.update()
    update_bg()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    # for end of level
    if endState == 1:
        winText = FONT_WIN_LOSE.render("YOU WIN", True, (0, 0, 0))
        SURFACE.blit(winText, (HEIGHT / 2, WIDTH / 2))
        if (pygame.time.get_ticks() - text_time) > 3000:
            endState = 0
            time = 0
            level_num = level_num + 1
            resetPlayers()

    elif endState == -1:
        loseText = FONT_WIN_LOSE.render("YOU LOSE", True, (0, 0, 0))
        SURFACE.blit(loseText, (HEIGHT / 2, WIDTH / 2))
        if (pygame.time.get_ticks() - text_time) > 3000:
            endState = 0
            time = 0
            event.type = QUIT

    # for timer
    time = time + 1
    timer(time)
    level(level_num)

    # updating the textures
    allSprites.update()
    allSprites.draw(SURFACE)
    pygame.display.update()
    # tick frame
    framePerSec.tick(FPS)