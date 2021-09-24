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
WIDTH = 300
HEIGHT = 300

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

#defined classes
class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((300, 10))
        self.surf.fill(GREEN)
        self.rect = self.surf.get_rect(center = (150, 295))

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.surf = pygame.Surface((10, 10))
        self.surf.fill(BLACK)
        self.rect = self.surf.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.w = 10
        self.rect.h = 10
        self.vx = 0
        self.vy = 0
        self.jump = True

    def update(self):
        dx = 0;
        dy = 0;
        #input
        key=pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx -= 5
        if key[pygame.K_RIGHT]:
            dx += 5
        if key[pygame.K_UP]:
            if (self.jump):
                self.jump = False
                self.vy = -15
    
        #gravity
        dy += self.vy
        self.vy = min(self.vy + 1, 10)
        
        #testing
        new_rect = pygame.Rect(self.rect.x+dx, self.rect.y+dy, self.rect.w, self.rect.h)
        if(new_rect.y >= HEIGHT - new_rect.h):
            self.vy = 0
            self.jump = True
        self.rect = new_rect.clamp(pygame.Rect(0,0, WIDTH, HEIGHT))
        #drawing        

def update_bg():
    SURFACE.fill(LIGHT_BLUE)
    #caption display
    pygame.display.set_caption('Test Game')

    #drawing mountain background
    pygame.draw.polygon(SURFACE, GREY, [(0, HEIGHT), (WIDTH/2, 0), (WIDTH, HEIGHT)])
    pygame.draw.polygon(SURFACE, WHITE, [(int(WIDTH/3), int(HEIGHT/3)), (int(WIDTH/2), 0),
                                         (int(WIDTH * (2/3)), int(HEIGHT/3))])

    #drawing platforms
    pygame.draw.line(SURFACE, LIGHT_GREY, (50, 250), (150, 250), 10)
    pygame.draw.line(SURFACE, LIGHT_GREY, (170, 200), (245, 200), 10)

    #end flag
    pygame.draw.line(SURFACE, BLACK, (110, 125), (110, 105), 3)
    pygame.draw.polygon(SURFACE, RED, [(109, 115), (102, 115), (109, 105)])

    #last platform
    pygame.draw.line(SURFACE, LIGHT_GREY, (100, 125), (175, 150), 10)

    #start flag
    pygame.draw.line(SURFACE, BLACK, (25, 290), (25, 270), 3)
    pygame.draw.polygon(SURFACE, RED, [(24, 280), (17, 280), (24, 270)])

    #drawing ground level
    #pygame.draw.line(SURFACE, GREEN, (0, 295), (300, 295), 10)

# initializing the pygame
pygame.init()

ground = Ground()
player = Player(150, 150)

allSprites = pygame.sprite.Group()
allSprites.add(ground)
allSprites.add(player)

#game running
while True:
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    update_bg()
    for entity in allSprites:
        entity.update()
        SURFACE.blit(entity.surf, entity.rect)
    pygame.display.update()
    framePerSec.tick(FPS)