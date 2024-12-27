import pygame as pg
import sys
import random

pg.init()
# pg.mixer.init()
print("starting")
# display screen and basic set up
width = 1280
height = 720
resolution = (width, height)
screen = pg.display.set_mode(resolution, pg.RESIZABLE)
clock = pg.time.Clock()

#LOAD ALL IMAGES:

#Background images:
bg_List = [
            pg.image.load("graphics/sky.png").convert_alpha(),
            pg.image.load("graphics/bgBuildings.png").convert_alpha(),
            pg.image.load("graphics/bgPowerLines.png").convert_alpha(),
            pg.image.load("graphics/bgBirds.png").convert_alpha()
            ]

class World():
    
    def __init__(self, imgSelect, bgspeed = 0):
        imgSelect = imgSelect
        bgspeed = bgspeed
        self.reset(imgSelect, bgspeed)

    def reset(self, imgSelect, bgspeed):

        self.bgSelect = imgSelect

        # SCALE DOWN img:
        "as long as the backgrounds are the same size this is ok if not then need to do logic similar to player animation"
        # self.ratio = 1280*3 = 3840
        scaleNum = 1/2 #change this to scale original image
        self.imgSize = self.bgSelect.get_size()
        self.imgScaled = (self.imgSize[0]*scaleNum, self.imgSize[1]*scaleNum) #all images should be the same sie or else this wont work
        img = pg.transform.smoothscale(self.bgSelect, self.imgScaled)

        #final after all mods
        self.background = img

        #starting position of background
        self.bgStartPosx = 0 #this will be used to scroll
        self.bgStartPosy = 0 #this probably won't need to change

        self.bgRect = pg.Surface.get_rect(self.background)
        self.bgRect.topleft = (self.bgStartPosx, self.bgStartPosy)

        #for movement
        self.bgMove = False
        self.kMoveBool = False

        if bgspeed == None:
            pass
        elif bgspeed == "":
            pass
        elif abs(bgspeed) > 0:
            self.kMoveBool = True
            self.bgSpeed = bgspeed
            # print("here:", bgspeed)
        elif bgspeed == 0:
            self.kMoveBool = False

    def update(self):

        if self.bgMove == True and self.kMoveBool == False:
            self.bgStartPosx -= self.bgSpeed#abs(player.dx)/6#+
            # if player.dx == 0:
            #     self.bgMove = False
        elif self.kMoveBool == True:
            self.bgStartPosx -= self.bgSpeed

        #if the background has fully scrolled off the screen, reset position
        if self.bgStartPosx <= -self.background.get_width():
            self.bgStartPosx = 0

    def draw(self):
        screen.blit(self.background, (self.bgStartPosx, self.bgStartPosy))
        screen.blit(self.background, (self.bgStartPosx+self.background.get_width(), self.bgStartPosy)) #twice for seamless repetition

#instantiate world
sky = World(bg_List[0], 0.25)
world = World(bg_List[1],3)
bgPowerLines = World(bg_List[2],3)
bgBirds = World(bg_List[3],0.55)

gameActive = True
running = True

while running:
    for event in pg.event.get():

        if event.type == pg.QUIT:
            pg.quit() #opposite of pg init
            sys.exit(0) #stops while loop and ends cleanly
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit(0) 
    if gameActive:
         #background and text
        sky.update()
        bgBirds.update()
        world.update()
        bgPowerLines.update()  
        sky.draw()
        bgBirds.draw()
        world.draw()
        bgPowerLines.draw() #placed after npc to hide him behind the power lines

        #refreshes the screen with a frame rate of 60Hz
        pg.display.flip()
        clock.tick(60)