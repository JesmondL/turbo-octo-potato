import pygame, sys, time

from pygame.locals import *

# define colors
AQUA = (  0, 255, 255)
BLACK = (  0,   0,   0)
BLUE = (  0,  0, 255)
FUCHSIA = (255,   0, 255)
GRAY = (128, 128, 128)
GREEN = (  0, 128,   0)
LIME = (  0, 255,   0)
MAROON = (128,  0,   0)
NAVY_BLUE = (  0,  0, 128)
OLIVE = (128, 128,   0)
PURPLE = (128,  0, 128)
RED = (255,   0,   0)
SLIVER = (192, 192, 192)
TEAL = (  0, 128, 128)
WHITE = (255, 255, 255)
YELLOW = (255, 255,   0)

# always need after importing the pygame module
# and before calling any other pygame function
pygame.init()

# frame per second
FPS = 30
fpsClock = pygame.time.Clock()

# return the pygame.Surface object for the window
DISPLAYSURFACE = pygame.display.set_mode((400,300),0,32)
# window name
pygame.display.set_caption('Animation')

# paint on surface object
DISPLAYSURFACE.fill(WHITE)

# draw shape
pygame.draw.polygon(DISPLAYSURFACE,GREEN,((146,0),(291,106),(237,277)
                                          ,(56,277),(0,106)))
pygame.draw.line(DISPLAYSURFACE, BLUE, (60, 60), (120, 60), 4)
pygame.draw.circle(DISPLAYSURFACE, BLUE, (300, 50), 20, 0)
pygame.draw.ellipse(DISPLAYSURFACE, RED, (300, 250, 40, 80), 1)
pygame.draw.rect(DISPLAYSURFACE,RED,(200,100,100,50))
pygame.draw.aaline(DISPLAYSURFACE,BLACK,(5,5),(25,25),4)# anti-aliasing line

# image
carImg = pygame.image.load('Resources/Shell_Concept_Car.jpg')
car_x = 50
car_y = 50
direction = 'right'

# font
fontObj = pygame.font.Font('Fonts/DroidSansMono.ttf',16)
textSurfaceObj = fontObj.render('Hello World', True, WHITE, BLUE)
textRectObj = textSurfaceObj.get_rect()
textRectObj.center = (200,20)

# sound trigger play method
#soundObj = pygame.mixer.Sound('Sounds/Somnus.mp3')
#soundObj.play()
#soundObj.stop()
# sound background play method
pygame.mixer.music.load('Sounds/Somnus.mp3')
pygame.mixer.music.play(-1,0.0)# -1 = forever loop


while True:
    if direction == 'right':
        car_x += 5
        if car_x == 150:
            direction = 'down'
    elif direction == 'down':
        car_y += 5
        if car_y == 200:
            direction = 'left'
    elif direction == 'left':
        car_x -= 5
        if car_x == 50:
            direction = 'up'
    elif direction == 'up':
        car_y -= 5
        if car_y == 50:
            direction = 'right'

    DISPLAYSURFACE.blit(carImg, (car_x, car_y))
    DISPLAYSURFACE.blit(textSurfaceObj, textRectObj)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    fpsClock.tick(FPS)