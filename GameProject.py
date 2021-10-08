#NEED TO TURN THE LEVEL DESIGN INTO RATIOS
#PUT PLATFORMS INTO ARRAY

# importing libraries
import pygame
from pygame.locals import *
import sys

#assigning constants
#set fps
FPS = 30
framePerSec = pygame.time.Clock()

#set frame
WIDTH = 450
HEIGHT = 400

#color
BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 255)
LIGHT_BLUE = pygame.Color(40, 175, 255)
GREEN = pygame.Color(0, 255, 0)
GREY = pygame.Color(90, 90, 90)
LIGHT_GREY = pygame.Color(170, 170, 170)
RED = pygame.Color(255, 0, 0)
WHITE = pygame.Color(255, 255, 255)

SURFACE = pygame.display.set_mode((WIDTH, HEIGHT))

'''
The ground for the game, unique sprite
outputs: a sprite object that needs to be created and added to the sprites group
'''
class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([WIDTH, HEIGHT-(HEIGHT-10)])
        #self.surf = pygame.Surface((WIDTH, HEIGHT-(HEIGHT-10)))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center = (WIDTH/2, HEIGHT-5))

'''
The platforms throughout the level
inputs: xLoc = the left most location, yLoc = the top most location, width = the length of the platform
outputs: a sprite object that needs to be created and added to the sprites group
'''
class Platform(pygame.sprite.Sprite):
    def __init__(self, xLoc, yLoc, width):
        super().__init__()
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
        self.image = pygame.Surface((WIDTH/100, (2*HEIGHT)/25))
        self.image.fill(BLACK)
        pygame.draw.rect(self.image, BLACK, pygame.Rect(xLoc, yLoc, WIDTH/100, HEIGHT/60))
        self.rect = self.image.get_rect(left = xLoc, top = yLoc)

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
        self.vx = 0
        self.vy = 0
        self.jump = False

    def update(self):
        dx = 0;
        dy = 0;
        #collison for player
        
        #input
        key=pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx -= 5
        if key[pygame.K_RIGHT]:
            dx += 5
        if key[pygame.K_UP]:
            if (self.jump):
                self.vy = -10
    
        #gravity
        dy += self.vy
        self.vy = min(self.vy + 1, 10)
        self.rect.x += dx
        self.rect.y += dy
        self.rect = self.rect.clamp(0,0,WIDTH,HEIGHT)
        hits = pygame.sprite.spritecollide(player, platforms, False)
        if hits:
            self.rect.y = hits[0].rect.top - self.rect.h
            self.vy=0;
            self.jump = True
        else: 
            self.jump = False


def update_bg():
    SURFACE.fill(LIGHT_BLUE)
    #caption display
    

    #drawing mountain background
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH/2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH/3), int(HEIGHT/3)), (int(WIDTH/2), 0),
                                         (int(WIDTH * (2/3)), int(HEIGHT/3))])

    #end flag, remains static
    pygame.draw.polygon(SURFACE, RED, [((11*WIDTH)/30, (23*HEIGHT)/60), ((17*WIDTH)/50, (23*HEIGHT/60)), ((11*WIDTH)/30, (7*HEIGHT)/20)])


    #start flag, remains static
    pygame.draw.polygon(SURFACE, RED, [((2*WIDTH)/25, (14*HEIGHT)/15), ((17*WIDTH)/300, (14*HEIGHT)/15), ((2*WIDTH)/25, (9*HEIGHT)/10)])

    #drawing ground level
    #pygame.draw.line(SURFACE, GREEN, (0, 295), (300, 295), 10)

# initializing the pygame
pygame.init()
pygame.display.set_caption('Test Game')

ground = Ground()
player = Player(150, 150)
#platform numbers go from the top so the platform that has the end flag is the highest number
platform1 = Platform(WIDTH / 6, (HEIGHT*5) / 6, WIDTH / 3)
platform2 = Platform(WIDTH/2, (2*HEIGHT)/3, WIDTH / 3)
platform3 = Platform(WIDTH/3, (HEIGHT*5)/12, WIDTH / 4)
endFlag = FlagPole((WIDTH*11)/30, (HEIGHT*7)/20)
startFlag = FlagPole(WIDTH/12, (9*HEIGHT)/10)

#to update all the sprites
allSprites = pygame.sprite.Group()
#for collsion
platforms = pygame.sprite.Group()
allSprites.add(ground)
allSprites.add(player)
allSprites.add(platform1)
allSprites.add(platform2)
allSprites.add(platform3)
allSprites.add(endFlag)
allSprites.add(startFlag)
platforms.add(ground)
platforms.add(platform1)
platforms.add(platform2)
platforms.add(platform3)

#game running
while True:
    #pygame.display.update()
    update_bg()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    
    #for entity in allSprites:
    #entity.update()
    allSprites.update()
    allSprites.draw(SURFACE)
    pygame.display.update()
    framePerSec.tick(FPS)