import asyncio          # pygbag needs an async main loop (see main() at the bottom)
import pygame as pg
import sys, os
import random
import json, time


#Dev Notes:
# right now it is working push these changes. 12/26/2024
# To Do:
#Add collision detection so that the skater can grind the objects
"Might have to do with the new values. maybe change to integers or add in main menu and other stuff to handle end game stuff" #mostly fixed with event queue
#Edit the jump height to be a percentage of what it was with floor division #done
#fix display issue of items


def resource_path(relative_path):
    """Get the absolute path to a resource, works for Pygbag and local."""
    try:
        # For WebAssembly (Pygbag)
        base_path = sys._MEIPASS
    except AttributeError:
        # For local execution
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pg.init()
pg.mixer.init()
# display screen and basic set up
width = int(1280 *0.625)
height = int(720 *0.625)
resolution = (width, height)
screen = pg.display.set_mode(resolution) #, pg.RESIZABLE
# On a phone held upright the window gets taller (the touch pads live under the game), so we keep
# track of the real window surface (`display`), the part the game is drawn on (`gameSurface`) and
# the window height (`displayH`). `screen` stays what the rest of the game draws to.
display = gameSurface = screen
displayW = width      # window width  (wider than the game when the landscape side bars are used)
displayH = height     # window height (taller than the game when the phone is upright)
barOffset = 0         # width of one side bar (0 = no side bars)
clock = pg.time.Clock()


#fonts for displaying text
textFont1 = pg.font.Font(None, int(50*0.625)) # None can be changes to specify a font type
textFont2 = pg.font.Font(None, int(25*0.625)) # 25 is a smaller font size than the above

# ---------------------------------------------------------------------------
# PERFORMANCE HELPERS
# ---------------------------------------------------------------------------
# The game was tuned at 60 frames per second, and all movement is "per frame".
# On a slow computer/phone the frame rate drops and everything ran in slow motion
# (and jumps changed height). The main loop now always advances the game in fixed
# 1/60 s steps, so speed is identical on every device. If a device is too slow it
# draws fewer frames instead of slowing the game down.
FIXED_DT = 1 / 60
MAX_STEPS_PER_FRAME = 4      # never try to catch up more than this many steps in one frame
MAX_FRAME_TIME = 0.25        # ignore long pauses (tab switch etc.)

# ---------------------------------------------------------------------------
# FEEL / TUNING  (the values you asked for after play-testing; change them here)
# ---------------------------------------------------------------------------
MAX_SPEED = 11.2              # was 14  (80%)
ACCELERATION = 0.35/3         # was 0.35/2  (takes a bit longer to reach top speed)
OLLIE_SCALE = 0.866           # was 1.0. Jump height goes with the square of this: 0.866 -> 75% height

# font.render() is slow (especially in the browser). Text that doesn't change is
# rendered once and re-used.
_textCache = {}
def renderText(font, text, color):
    key = (id(font), text, color)
    surf = _textCache.get(key)
    if surf is None:
        if len(_textCache) > 300:
            _textCache.clear()
        surf = font.render(text, True, color)
        _textCache[key] = surf
    return surf

#Version control

versionSurf = textFont2.render("Version: 0.3.3", True, "white")


# listFonts = pg.font.get_fonts()
# print(listFonts)
"we could make this a list of fonts and use an index to select between them"

#setting the display window caption
pg.display.set_caption("Skater Kitty")


#loading all the images
# disp_icon = pg.image.load(resource_path("graphics/HeadofKittyBoardBluntLoyalton.png")).convert_alpha()

#place images to respective locations
# pg.display.set_icon(disp_icon) #load it to the display window

#starting positions
player_xPos = int(250 *0.625)
player_yPos = int(675 *0.625)
player_xPos1 = 1280
player_yPos1 = 675

#setting up booleans
running = True
gameActive = False

#LOAD ALL IMAGES:

#Background images:
# sky has no transparency -> convert() makes it a fast opaque copy instead of a slow alpha blend.
# The power lines and birds layers were cropped to just the rows that contain artwork
# (the empty transparent rows were being blended every frame for nothing). BG_Y is where
# the cropped layer sits on screen, so it looks exactly the same as before.
bg_List = [
    pg.image.load(resource_path("graphics/sky.jpg")).convert(),
    pg.image.load(resource_path("graphics/bgBuildings.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/bgPowerLines.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/bgBirds.png")).convert_alpha()
    ]
BG_Y = [0, 0, 125, 12]

skatepart_imgs = [
    pg.image.load(resource_path("graphics/wheel.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/wheelPack.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/trucks.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/truckPack.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/bearings.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/boardDeck.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/boardSideViewL.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/boardGripTape.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/completeDeck.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/boardSideViewR.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/bearingsDisp.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/boardDeckDisp.png")).convert_alpha(),
    ]

button_imgs = [
    pg.image.load(resource_path("graphics/playBlueButton3.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/controlsButton.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/menuButtonBlue.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/objectiveButton.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/playAgainButton.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/youWinButton.png")).convert_alpha()
    # pg.image.load(resource_path("graphics/youWinButtonB.png")).convert_alpha()

    ]

playerImgs = [
    pg.image.load(resource_path("graphics/player1.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/player2.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/player3.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/player4.png")).convert_alpha()
]

cashImg = pg.image.load(resource_path("graphics/cash.png")).convert_alpha()
statsMenuImg = pg.image.load(resource_path("graphics/statsMenu.png")).convert_alpha()
imgConfetti = pg.image.load(resource_path("graphics/winConfetti.png")).convert_alpha()

mainMenuImgs = [
    pg.image.load(resource_path("graphics/gameName5.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/controlsMenu.png")).convert_alpha(),
    pg.image.load(resource_path("graphics/objectiveMenu.png")).convert_alpha(),
]

# #Import Audio Files:
# rolling = pg.mixer.Sound("audio/rolling.wav")
ambientSound = pg.mixer.Sound("audio/ambientOutdoorSounds.ogg")
cashSound = pg.mixer.Sound("audio/cash.ogg")
#skateboard sounds
ollieUpSound = pg.mixer.Sound("audio/ollieUp.ogg")
ollieDownSound = pg.mixer.Sound("audio/ollieDown.ogg")
rollingSound = pg.mixer.Sound("audio/rollingshort.ogg")
specialCollectSound = pg.mixer.Sound("audio/specialItemSound.ogg")
specialCollectSound.set_volume(0.25)

#bail sounds
livBailVoice = pg.mixer.Sound("audio/livCrashVoice.ogg")
# dorBailVoice = pg.mixer.Sound("audio/dorCrashVoice.ogg")
boardHitObj = pg.mixer.Sound("audio/boardHitObj.ogg")
bailSound = pg.mixer.Sound("audio/bailSoundBoard.ogg")
bailSoundTopple = pg.mixer.Sound("audio/bailSoundBoardTopple.ogg")

grindLand = pg.mixer.Sound("audio/grindLandMetal.ogg")
grindLandSlide = pg.mixer.Sound("audio/grindLandSlideRail.ogg")
grindSlide = pg.mixer.Sound("audio/grindSlideMetal.ogg")
grindPack = [grindLand, grindLandSlide, grindSlide]

# #play sound
# The music streams from disk instead of being fully decoded into memory (saves ~20 MB of RAM).
def startMusic():
    """Start (or restart) the background music and the ambient street sound."""
    global bgMusic
    try:
        pg.mixer.music.load("audio/RomanoBeatbyLoyalton.ogg")
        pg.mixer.music.play(-1) #-1 means to loop indefinitely
    except Exception:
        bgMusic = pg.mixer.Sound("audio/RomanoBeatbyLoyalton.ogg")
        bgMusic.play(-1)
    ambientSound.play(-1)
    ambientSound.set_volume(0.05)
startMusic()


class World():
    
    def __init__(self, imgSelect, bgspeed = 0, yOffset = 0):
        imgSelect = imgSelect
        bgspeed = bgspeed
        self.yOffset = yOffset
        self.reset(imgSelect, bgspeed)

    def reset(self, imgSelect, bgspeed):

        self.bgSelect = imgSelect

        # SCALE DOWN img:
        "as long as the backgrounds are the same size this is ok if not then need to do logic similar to player animation"
        # self.ratio = 1280*3 = 3840
        # scaleNum = 1/2 #change this to scale original image
        # self.imgSize = self.bgSelect.get_size()
        # self.imgScaled = (self.imgSize[0]*scaleNum *0.625 // 1, self.imgSize[1]*scaleNum *0.625 // 1) #all images should be the same sie or else this wont work
        # img = pg.transform.smoothscale(self.bgSelect, self.imgScaled)

        #final after all mods
        self.background = imgSelect

        #starting position of background
        self.bgStartPosx = 0 #this will be used to scroll
        self.bgStartPosy = self.yOffset #cropped layers sit lower on the screen
        self.bgW = self.background.get_width()

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
            self.bgStartPosx -= abs(player.dx)/6#+self.bgSpeed
            if player.dx == 0:
                self.bgMove = False
        elif self.kMoveBool == True:
            self.bgStartPosx -= self.bgSpeed

        #if the background has fully scrolled off the screen, reset position
        if self.bgStartPosx <= -self.bgW:
            self.bgStartPosx = 0

    def draw(self):
        screen.blit(self.background, (self.bgStartPosx, self.bgStartPosy))
        if self.bgStartPosx + self.bgW < width: #second copy only when it is actually on screen
            screen.blit(self.background, (self.bgStartPosx+self.bgW, self.bgStartPosy)) #twice for seamless repetition

class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def reset(self, x, y):

        self.img = self.ollieImages = playerImgs
        self.current_image_index = 0
        # self.player_TranformedList = []

        # for index in range(len(self.img)):
        #     self.imgSelect = self.ollieImages[index] #self.current_image_index
        #     self.scaleNum = 1/13 #change this to scale original image
        #     self.imgSize = self.imgSelect.get_size()  #original image size
        #     new_width = int(self.imgSize[0] * self.scaleNum)
        #     new_height = int(self.imgSize[1] * self.scaleNum)
        #     self.imgScale = (new_width, new_height)
        #     self.player = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        #     self.player_TranformedList.append(self.player)

        # self.player = self.player_TranformedList[self.current_image_index]
        self.player = self.img[self.current_image_index]

        self.playerRect = self.player.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.playerRect.midbottom = (x,y)
        self.width = self.player.get_width()
        self.height = self.player.get_height()

        #Bools and counters
        self.ollieAnimationSpeed = 6
        self.ollieCounter = 0
        self.gravity = 0
        self.gravityBool = False
        self.readyJumpBool = True
        self.inAirBool = False
        self.spaceBarHeld = False
        self.counterFrame = 0
        self.grindBool = False
        self.bailBool = False
        self.shiftPressed = False
        self.grindKeyBool = False
        self.loseConditionBool = False
        self.platformBool = False

        #mobile bools
        self.jumpMobile = False
        
        #counter for speed and accelleration control
        self.dx = 0
        self.dy = 0
        self.acceleration = ACCELERATION
        self.deceleration = 0.05
        self.max_speed = MAX_SPEED
        self.movingRight = False
        self.movingLeft = False
        self.RailOllie = False
        self.ollieHeight = 23


        #bools for Sound
        self.playRolling = False

        #temp rect
        self.tempPosAdj = 20*0.625
        self.tempRectx = pg.rect.Rect(self.playerRect[0]+self.tempPosAdj, self.playerRect[1]-self.tempPosAdj, self.playerRect.w, self.playerRect.h)
        self.tempRectx.bottom = self.playerRect.bottom

        self.tempRecty = pg.rect.Rect(self.playerRect[0], self.playerRect[1]+self.tempPosAdj, self.playerRect.w, self.playerRect.h)
        self.tempRecty.right = self.playerRect.right
        pass

    def playerMotion(self):
        #control acceleration to the right
        if self.movingRight:
            if self.dx < self.max_speed:
                self.dx += self.acceleration
                pass
            else:
                self.dx = self.max_speed  #cap speed at max_speed
                pass
            self.movingRight = False

        #control acceleration to the left           
        elif self.movingLeft:
            if self.dx > -self.max_speed:
                self.dx -= self.acceleration*1.5
                if self.dx <= 0: #with frame of foot out will bring to a stop
                    self.dx = 0
                pass
            else:
                self.dx = -self.max_speed #this is no longer in use cause player static and bg moves with abs(dx)
                pass
            self.movingLeft = False

        #decelerate if no keys are being pressed
            "right now this is at a different dx than moving right SLOWER"
        else:
            if self.dx > 0:
                self.dx -= self.deceleration  # Decelerate to the right
                if self.dx < 0:  #stops at 0
                    self.dx = 0
                    pass
            elif self.dx < 0:
                self.dx += self.deceleration  # Decelerate to the left
                pass
                if self.dx > 0: 
                    self.dx = 0

        self.playSound() #go to method to play sound based on state of game


        
        #Movement keys and setting other object and world Bools 
        "the section below needs added logic for tricks if time"   
        if keys[pg.K_d]:
            self.movingRight = True           
            world.bgMove = True
            bgPowerLines.bgMove = True
            obstacle1.obstacleMove = True

        else:
            # self.playerRect.right += self.dx
            pass

        if keys[pg.K_a]:
            # self.playerRect.left += self.dx
            self.movingLeft = True           
            world.bgMove = True
            bgPowerLines.bgMove = True
            # rolling.play()
        if keys[pg.K_w]:
            # self.playerRect.top += -10
            pass
        if keys[pg.K_s]:
            # self.playerRect.bottom += 10
            pass
    
    def playSound(self):
        self.maxVolume = 0.5
        # adjust volume setting based on dx
        self.volume = max(0, min(abs(self.dx) / self.max_speed, self.maxVolume))
        # print(abs(self.dx) / self.max_speed)
        #playing sound based on motion
        if self.dx > 0 and self.inAirBool == False:
            if self.playRolling == False:
                # rollingSound.set_volume(0.15)
                rollingSound.play(-1)  # Play in loop mode
            self.playRolling = True #makes it so only sets loop one time
            rollingSound.set_volume(self.volume/3)
        # elif self.movingLeft == True:
        #     rollingSound.fadeout()
        else:
            if self.playRolling == True:
                rollingSound.stop()
            self.playRolling = False
                

    def playerInput(self, dt):
        self.ollieHeight = OLLIE_SCALE * min(1500*dt-4, player_yPos-(width/2)+4) #ollie height difference based on dt for web(perfer fixed) vesus local (perfer dt)
        # self.playerMotion()       

        #CONTROLS by USER INPUT
        "this is one way to do it but we can also use the event queue. Which is better?"
        keys = pg.key.get_pressed()

        #--------------------------------------------------------
        #JUMP AND ANIMATION LOGIC:
        if self.playerRect.bottom >= player_yPos: #later this will be changes to collision logic for surfaces
            #should also be true if collide with top of objects and hit grind or ride platforms
            self.readyJumpBool = True
        else:
            self.readyJumpBool = False

        if keys[pg.K_SPACE] or self.jumpMobile == True:
            if self.readyJumpBool == True and self.inAirBool == False: #and self.spaceBarHeld == True:
                self.readyJumpBool = False  # Disable further jumps until landing
                self.spaceBarHeld = True  # Update space hold flag
            else:
                pass
        #check if the space bar is released
        else:
            if self.spaceBarHeld:  # If space was just released
                self.gravityBool = True
                # print(self.playerRect.midbottom[1])
                self.gravity = -self.ollieHeight #25 UNCOMMENT used to be 25 when resolution was full
                ollieUpSound.play()
                ollieUpSound.set_volume(0.5)
                self.inAirBool = True
            self.spaceBarHeld = False
        #--------------------------------------------------------

        # if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
        #     self.grindKeyBool = True
        # else:
        #     self.grindKeyBool = False

        if self.shiftPressed:
            self.grindKeyBool = True
        else:
            self.grindKeyBool = False


    def collision(self, rect, currPosPass):
        
        if obstacle1.ObstacleRect.colliderect(self.tempRectx):
            # rollingSound.stop()
            
            if obstacle1.ObstacleRect.left < self.playerRect.right-25*0.625: #adjust num if needed -25 is good
                pass

            elif obstacle1.ObstacleRect.left <= self.playerRect.right:
                "BAIL IN X POS"
                # print("BAIL!!!!!!!!!!!!!!!!!!!!!!!")
                "there may be a condition where this falsely triggers but I think it's ok for now"
                rollingSound.stop()
                self.dx = 0
                self.loseConditionBool = True
                # print("loseloselose in x dir", self.loseConditionBool)
                "issue: triggered but not ending game" #Resolved was due to elif below was only if
                "ADD BAIL SOUND HERE"
                
                if self.bailBool == False:
                    # rollingSound.set_volume(0.15)
                    # grindLand.play()
                    boardHitObj.play()
                    livBailVoice.play()  # Play in loop mode
                    # dorBailVoice.play()
                    pass
                self.bailBool = True #makes it so only sets loop one time
                livBailVoice.set_volume(self.volume/2)

            else:
                self.gravityBool = False 
                # self.inAirBool = False

        # "leave this below line as if-statement to always check for both but be aware of above comment ^" not needed anymore
        elif obstacle1.ObstacleRect.colliderect(self.tempRecty):
            # rollingSound.stop()
            # if self.playerRect.bottom > obstacle1.ObstacleRect.top+20 and self.grindKeyBool == False: #bail vert range
            #     print("collided rect")
            # if self.playerRect.left+40 < obstacle1.ObstacleRect.right:
                    
            #     if obstacle1.ObstacleRect.left > self.playerRect.left: #bail range
            #         "BAIL"
            #         print("BAIL!!!!!!!!!!!!")
            #         self.loseConditionBool = True
            #     pass

            "couldn't get platform logic to work try later when time allows"
            # if self.platformBool == True: #"add if the obstacle right stair portion not included"
            #     print("go on top of platform")


            #     if keys[pg.K_SPACE]:
            #         # self.inAirBool = False
            #         ollieUpSound.play()
            #         self.gravity = -25
            #         self.current_image_index = 1 #cycle the image index back resolved the bug!
            #         self.RailOllie = True #to be able to ollie while on the rail still
            #         self.change_image(self.current_image_index, self.curPos)
            #         # self.platformBool = False
            #         # self.inAirBool = False

            #     if self.RailOllie == False or self.current_image_index == 3: # or self.current_image_index == 0 :
            #         # # self.grindBool = True
            #         # self.playerRect.bottom = obstacle1.ObstacleRect.top+8
            #         # self.current_image_index = 0 #cycle the image index back resolved the bug!
            #         # self.RailOllie = True #to be able to ollie while on the rail still
            #         # self.change_image(self.current_image_index, self.curPos)
            #         # self.tempRecty.midbottom = self.playerRect.midbottom
            #         self.gravity = 0 
            #         self.gravityBool = False 
            #         self.inAirBool =False               
            #         self.readyJumpBool = True

            #     pass
            if obstacle1.ObstacleRect.top+40*0.625 > self.playerRect.bottom > obstacle1.ObstacleRect.top and self.grindKeyBool == True: #used to be 20 no 40
                # print("vert")
                rollingSound.stop()
                "grind enable Vertical range "
                if keys[pg.K_SPACE]:
                    # self.inAirBool = False
                    ollieUpSound.play()
                    self.gravity = -self.ollieHeight
                    self.current_image_index = 1 #cycle the image index back resolved the bug!
                    self.RailOllie = True #to be able to ollie while on the rail still
                    self.change_image(self.current_image_index, self.curPos)
                else:
                    # self.grindBool = True
                    self.playerRect.bottom = obstacle1.ObstacleRect.top+8
                    # self.tempRecty.midbottom = self.playerRect.midbottom
                    self.gravity = 0 
                    self.gravityBool = False 
                    # self.inAirBool =False               
                    self.readyJumpBool = True

                if self.dx > 0 and self.inAirBool == True:
                    # self.grindBool = True
                    if self.grindBool == False:
                        # rollingSound.set_volume(0.15)
                        # grindLand.play()
                        grindLandSlide.play()  # Play in loop mode
                    self.grindBool = True #makes it so only sets loop one time
                    grindLandSlide.set_volume(self.volume)
                # elif self.movingLeft == True:
                #     rollingSound.fadeout()
                else:
                    # print("in else statement")
                    if self.grindBool == True:
                        grindLandSlide.stop()
                    self.grindBool = False
                    # self.inAirBool = False
                
                    # print(self.surf.get_width()*0.25) #=28.25 
                # print("in Vert grind range")
            
            else:
                if self.playerRect.bottom > obstacle1.ObstacleRect.top+20*0.625:
                    "TO DO: 11/10/2024"
                    " find a way to register the range that is out of bounds when exiting the grinding if statement above" #resolved
                    # print("Below grind range")

                    if self.playerRect.left+self.surf.get_width()*0.3< obstacle1.ObstacleRect.right:
                        # print("NOT safe range for exiting grind")
                        self.loseConditionBool = True
                        "ADD BAIL SOUND HERE"
                        if self.bailBool == False:
                            # rollingSound.set_volume(0.15)
                            # grindLand.play()
                            # bailSound.play()
                            bailSoundTopple.play()
                            livBailVoice.play()  # Play in loop mode
                            # dorBailVoice.play()
                        self.bailBool = True #makes it so only sets loop one time
                        livBailVoice.set_volume(self.volume/2)
                    else:
                        # print("Out of BAIL range")
                        self.playSound() #play rolling sound after grind logic bug fixed
                        pass

            # else:
            #     "BAIL"
            #     # print("BAIL!!!")
            #     self.loseConditionBool = True
        else:
            grindLandSlide.stop() #needed so when collision is not happening sound is stopped
            self.grindBool = False
            self.loseConditionBool = False
            pass

        if self.loseConditionBool == True:
            # print("BAIL!!!!!")
            grindLandSlide.stop()
            gameActive = False
            pass
    
    def animation(self, dt):
        # self.applyGravity() 
        # If space is held, use the first frame (image index 1)
        if self.spaceBarHeld and self.playerRect.bottom >= player_yPos: #ISSUE fix: check after player in air in issue is still there
            #also if on top of valid surface add that logic
            self.current_image_index = 1  # Use the second image (index 1)
            self.curPos = self.playerRect.midbottom
            self.change_image(self.current_image_index, self.curPos)
            # self.player = pg.transform.smoothscale(self.ollieImages[self.current_image_index], self.imgSize)
        
        elif self.inAirBool == True or self.RailOllie == True:

        #cycle through ollie images
            self.ollieCounter += 1*dt
            
            if self.ollieCounter >= self.ollieAnimationSpeed*dt:
                self.ollieCounter = 0
                if self.current_image_index < len(self.ollieImages) - 1:
                    self.counterFrame += 1*dt
                    self.current_image_index = 2
                    if self.counterFrame >= 1.5*dt: #used to be 3 change value to adjust how long slide up image is held
                        self.current_image_index += 1  #go to next image
                        self.counterFrame = 0
                else:
                    self.current_image_index = len(self.ollieImages) - 1  #hold last image until land
                    
                    if self.playerRect.bottom >= player_yPos:
                        self.inAirBool = False 
                        ollieDownSound.play()
                        ollieDownSound.set_volume(0.5)
            self.curPos = self.playerRect.midbottom
            self.change_image(self.current_image_index, self.curPos)
            self.RailOllie = False
                
            
        else:
            self.current_image_index = 0
            self.curPos = self.playerRect.midbottom
            self.change_image(self.current_image_index, self.curPos)
            pass            

    def applyGravity(self, dt):
        # print(self.gravity)
        self.gravity += 66*dt #63*dt,
        # print(self.gravity)
        # self.tempPos = (self.playerRect.y//1) 
        # self.playerRect.y = self.tempPos + self.gravity
        self.playerRect.y += self.gravity
        # self.dy = self.playerRect.y
        if self.playerRect.bottom >= player_yPos:
            self.playerRect.bottom = player_yPos
            self.gravityBool = False
            self.gravity = 0
            self.gravityBool = False

        #add collision detection for other obstacles


    def update_image(self, index, curPosPass):
        # self.applyGravity()
        self.curPosPass = curPosPass
        self.imgIndex = index
        self.imgSelect = self.img[self.imgIndex]

        # Scale the selected image
        # self.imgSize = self.imgSelect.get_size()
        # new_width = int(self.imgSize[0] * self.scaleNum*0.625 // 1)
        # new_height = int(self.imgSize[1] * self.scaleNum*0.625 // 1)
        # self.imgScale = (new_width, new_height)

        # scale and also update the rect dimensions based on new loaded image
        self.surf = self.player = self.imgSelect #pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.playerRect = self.player.get_rect()

        self.playerRect.midbottom = self.curPosPass#(player_xPos, self.currentPos[1])
        self.draw(self.surf, self.playerRect)

        #temp rect
        self.tempRectx = pg.rect.Rect(self.playerRect[0]+self.tempPosAdj, self.playerRect[1], self.playerRect.w, self.playerRect.h)
        self.tempRectx.bottom = self.playerRect.bottom-self.tempPosAdj

        self.tempRecty = pg.rect.Rect(self.playerRect[0], self.playerRect[1]+self.tempPosAdj, self.playerRect.w, self.playerRect.h)
        self.tempRecty.right = self.playerRect.right-self.tempPosAdj
        self.tempRecty.bottom = self.playerRect.bottom + self.tempPosAdj+5

    def change_image(self, new_index, curPos):
        # change image and draw new rect with correct dimensions no squashing or stretch
        if 0 <= new_index < len(self.img):
            self.update_image(new_index, curPos)

    def draw(self, surf, curPOSRect):
        
        "use three lines below to visualize for collision logic" #diasble for final game
        # pg.draw.rect(surface=screen, color="blue", rect=self.tempRectx, width=2)
        # pg.draw.rect(surface=screen, color="green", rect=self.tempRecty, width=2)
        # if self.shiftPressed:
        #     pg.draw.rect(screen, (255, 0, 0), self.playerRect, 2) #to visualize the rect around image
        

        screen.blit(surf, curPOSRect)
        


    def update(self, dt):
        #draw player onto screen
        self.curPosPass = self.playerRect.midbottom

        # pg.draw.rect(screen, (255, 0, 0), boardRect, 2)
        # self.playerInput()
        self.playerMotion()
        self.playerInput(dt)
        self.collision(self.playerRect, self.curPosPass)
        self.animation(dt)
        self.applyGravity(dt)
        
        # screen.blit(self.player, self.curPosPass)
        
        
        "if we want the character to move on the screen add these"
        # #BOUNDARIES: not in use if player doesn't move horizontally
        # if self.playerRect.right >= width:
        #     self.playerRect.right = width
        # if self.playerRect.left <= 0:
        #     self.playerRect.left = 0
        # # boardRect.midtop = (player.playerRect.midbottom[0]-10, player.playerRect.midbottom[1]-15)

class Obstacles():
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.reset(self.x,self.y)

    def reset(self, x,y):
        self.img = [
            #platforms:
            # pg.image.load(resource_path("graphics/blockandstairBlock.png"), # = 0 for list to check platform could use mapping

            # regular Obstacles
            pg.image.load(resource_path("graphics/rail.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/railTall.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/railLong.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/railLong2x.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/cementBlock.png")).convert_alpha(),
            
            pg.image.load(resource_path("graphics/cone.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/mailbox.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/meter.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/bench.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/barrier.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/bigCone.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/hydrant.png")).convert_alpha(),
            pg.image.load(resource_path("graphics/trashCan.png")).convert_alpha(),

        ]
        # print(len(self.img)-1)
        # self.img_List =[]
        # for index in range(len(self.img)):
        #     self.imgSelect = self.img[index]
        #     self.scaleNum = 1/6 #change this to scale original image

        #     self.imgSize = self.imgSelect.get_size()  # Original image size
        #     new_width = int(self.imgSize[0] * self.scaleNum)
        #     new_height = int(self.imgSize[1] * self.scaleNum)
        #     self.imgScale = (new_width *0.625, new_height *0.625)
        
        #     self.Obstacle = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        #     self.img_List.append(self.Obstacle)

        self.index = 0
        self.Obstacle = self.img[self.index]

        self.ObstacleRect = self.Obstacle.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.ObstacleRect.midbottom = (x,y)

        # self.randInt = random.randint(0, len(self.img)-1)
        self.obstacleMove = False
        self.resetting = False

    def draw(self):
        
        screen.blit(self.Obstacle, self.ObstacleRect)

    def update(self):

        if self.obstacleMove == True: #this is changed by player input K_d
            self.ObstacleRect.right -= abs(player.dx)
            # self.ObstacleRect.bottom = player_yPos

        if self.ObstacleRect.right <= 0 and not self.resetting:
            self.resetting = True
            self.randintx = random.randint(int(player_xPos), int(width*2))
            self.imgIndex = random.randint(0, len(self.img) - 1)
            self.change_image(self.imgIndex)
            self.ObstacleRect.left = width + self.randintx  # random pos of respawn
        elif self.ObstacleRect.right > 0:
            self.resetting = False

    
    def update_image(self, index):

        # self.imgSelect 
        self.Obstacle = self.img[index]
        self.ObstacleRect = self.Obstacle.get_rect()
        self.ObstacleRect.midbottom = (width, self.y)
        
    def change_image(self, new_index):
        # change image and draw new rect with correct dimensions no squashing or stretch
        if 0 <= new_index < len(self.img):
            self.update_image(new_index)

class NPC():
    def __init__(self, x, y):

        self.NPC1List = [
                    pg.image.load(resource_path("graphics/NPC1.png")).convert_alpha(),
                    pg.image.load(resource_path("graphics/NPC2.png")).convert_alpha()
                    ]
        # self.NPC1_index = 0
        self.NPCListNew = []
        self.NPCRectListNew = []
        for index in range(len(self.NPC1List)):
            self.NPC1_Select = self.NPC1List[index]
            # scaleNum = 1/25*0.625 #change this to scale original image
            # playerImageSize = self.NPC1_Select.get_size() #(240, 300)
            # self.playerScale = (playerImageSize[0]*scaleNum, playerImageSize[1]*scaleNum)
            # self.playerSize = (self.playerScale) #for rotozoom if you want 2x bigger just a 2, if use scale need tuple (100,100)

            # self.NPC = pg.transform.smoothscale(self.NPC1_Select, self.playerSize) #this is my new surface
            self.NPCListNew.append(self.NPC1_Select)

            self.NPCRect = self.NPCListNew[index].get_rect() #setting the bottom mid to a specific place dictated by start positions above
            self.NPCRect.midbottom = (self.NPCRect.x, height*6/7 -10*0.625)
            self.NPCRectListNew.append(self.NPCRect)
        
        self.startposx = 0
        self.NPC1 = self.NPCListNew[0]
        self.NPC1Rect = self.NPCRectListNew[0]
        self.NPC1Rect.x = x+self.startposx
        self.NPC1Rect.y = y-2
        


        # Time tracking variables
        #Switch between images
        self.last_switch_time = pg.time.get_ticks()  # To track when the last image switch happened
        self.switch_duration = 1000 # x second (for switching)
        self.normal_duration = 3000  # x seconds (between switches
        self.switched = False

        # Create bounce effect
        self.last_switch_time2 = pg.time.get_ticks()
        self.switch_duration2 = 100  # x second (for switching)
        self.normal_duration2 = 100 # x seconds (between switches
        self.switched2 = False

        self.respawned = False
        self.animationCounter = 0

    def animation(self, dt):
        #get the current time in milliseconds
        current_time = pg.time.get_ticks()
        # self.animationCounter += 1*dt
        self.tempPos = self.NPC1Rect.midbottom
        #if duration x seconds have passed, switch to the second image
        if not self.switched and current_time - self.last_switch_time > self.normal_duration:
            self.NPC1 = self.NPCListNew[0]
            self.NPC1Rect = self.NPC1.get_rect()
            self.last_switch_time = current_time  # Reset the timer
            self.switched = True  

        #if duration x seconds has passed in the switched state, return to the first image
        elif self.switched and current_time - self.last_switch_time > self.switch_duration:
            self.NPC1 = self.NPCListNew[1]
            self.NPC1Rect = self.NPC1.get_rect()
            self.switched = False

        #movement horizontally for npc
        self.NPC1Rect.midbottom = self.tempPos
        self.NPC1Rect.right -= abs(player.dx)/6 + 1#self.randInt
        return self.NPC1, self.NPC1Rect
        
    def update(self, dt):
        retObj = self.animation(dt)      
        self.NPC1, self.NPC1Rect =retObj[0], retObj[1]

        if self.NPC1Rect.x < -200 and not self.respawned:
            # Reset NPC position once
            self.respawned = True
            self.randInt = random.randint(0, 3)
            self.rantIntx = random.randint(player_xPos, width)
            self.NPC1Rect.left = width * (self.randInt + 2) + self.rantIntx

        # Reset the respawn flag once NPC is fully on screen
        if self.NPC1Rect.left > 0:
            self.respawned = False

        #draw player onto screen
        screen.blit(self.NPC1, self.NPC1Rect)
        # pg.draw.rect(screen, color="red", rect=self.NPC1Rect, width=2)
        
class EndScreen():

    def __init__(self, img):
        #creating text surfaces to blit later
        # gameNameSurf = textFont1.render("My Game!", True, 'Black') # second arg is for Anti Aliasing (smoothing edges) set to True or False
        "maybe not needed use button class instead"
        # self.scalenum = 0.30*0.625
        # self.img = pg.image.load(resource_path("graphics/statsMenu.png")).convert_alpha()
        # self.imgSize = self.img.get_size()
        # self.imgScaled = (self.imgSize[0]*self.scalenum, self.imgSize[1]*self.scalenum)
        # self.statsMenuSurf = pg.transform.smoothscale(self.img, self.imgScaled)
        self.statsMenuSurf = img
        self.statsMenuRect = self.statsMenuSurf.get_rect()
        self.statsMenuRect.center = (250*0.625, height-300*0.625)


        self.countEnd = 0
        self.maxEndCount = 75
        self.countBool = False
        self.endBool = False
        self.endGameTextSurf = textFont1.render("End Game!", True, (0,0,0))
        self.endGameTextSurf = textFont1.render("End Game!", True, (255,0,0))

        self.blinkTextRect = self.endGameTextSurf.get_rect()
        self.blinkTextRect.center = (width/2, height/2 -100*0.625)
        # self.finalScoreText = textFont1.render(f"Final Score: {displayScore()}", True, (255,0,0))

        self.playAgainTextSurf = textFont1.render("Press Enter/Return to play Again?", True, 'Black')

        # creating text rects
        self.playAgainTextRect = pg.Surface.get_rect(self.playAgainTextSurf)
        self.playAgainTextRect.center = (width/2, height*3/4)

        #animation counter for complete deck on end screen
        self.animationCounter = 0
        self.animationLimitNum = 20

        self.saveBool = False
        self.lines = ""
        self.dispScoreBool = False

    def blinkText(self, textSurf, color1= (0,0,0), color2= (255,0,0)):
        #setup
        self.blink_Text = textSurf
        self.blinkColor1 = color1
        self.blinkColor2 = color2

        #Blinking end text
        if self.countBool == False:
            self.countEnd += 1
        else:
            self.countEnd -= 1
        if self.countEnd == self.maxEndCount:
            self.countBool = True
        elif 0 < self.countEnd < self.maxEndCount and self.countBool == False:
            self.endGameTextSurf = renderText(textFont1, self.blink_Text, self.blinkColor1)
        elif 0 < self.countEnd < self.maxEndCount and self.countBool == True:
            self.endGameTextSurf = renderText(textFont1, self.blink_Text, self.blinkColor2)
        elif self.countEnd == 0:
            self.countBool = False
            pass
        blinkingSurf = self.blink_Text
        return blinkingSurf
    
    def saveLog(self):
        #later change this section to only save once the game has ended then update the endScreen()

        if self.saveBool == False:
            #save special skate parts
            # for item in range (0, len(spawnSpecialItemList) -1):
            #     self.lines = str(spawnSpecialItemList[item].finalItemcount)

            #     with open(f"saveParts{spawnSpecialItemList[item].imgIndex}.txt", mode="w", encoding="utf-8") as f:
            #         self.lines = f.writelines(self.lines)
            # self.saveBool = True

            # #save cash
            # self.lines = str(cash.cashcount)
            # with open("saveCash.txt", mode="w", encoding="utf-8") as f:
            #     self.lines = f.writelines(self.lines)

            # #save final time score
            # lines = displayScore()
            # with open("saveScore.txt", mode="w", encoding="utf-8") as f: #mode = "w" is for writing but clears wahatever data was there before
            #     lines = f.write(lines) #to read a single line
            #     # lines = f.writelines() #to read multiple lines

            # with open("saveScore.txt", mode="r", encoding="utf-8") as f: #mode = "r" is for reading saved files you can also open something in a folder with "name_of_folder\save.txt"
            #     # lines = f.read(8) #to read a single line if you give it a number in the arguement it gives you a number of characters
            #     lines = f.readlines() #to read multiple lines if you give it a number in the arguement up to that number in characters you get the first name up to n name
            #     finalscore = lines[0].strip() 
                # print(lines)
            # finalScoreText = textFont1.render(f'Final Time: {finalscore}s', True, ("blue"))
            
            if self.dispScoreBool == False:
                self.finalscore = displayScore()
                self.dispScoreBool = True
                leaderboard.onRunEnd(self.finalscore, cash.cashcount, finalSpecialItemCount())   # arcade top-3: asks for initials if needed
            self.finalScoreText = renderText(textFont1, f'{self.finalscore}', "blue")
            self.finalScoreRect = self.finalScoreText.get_rect(center = (350*0.625, height-300*0.625))
            # screen.blit(finalScoreText, finalScoreRect)
            pass



    def update(self, dt):
        self.saveLog()
        #update pos because main menu moves it out of the way
        playButton.buttonRect.center = (width/2, height/2)

        self.blinkText("END GAME!")    
        sky.update()
        bgBirds.update()
        sky.draw()
        bgBirds.draw()
        world.draw()
        nPC.update(dt)
        bgPowerLines.draw()

        completeDeckDisp.rect.center = (width*4/5, height*3/5)
        boardSideLDisp.rect.center = (width*4/5, height*3/5)
        boardGripTapeDisp.rect.center = (width*4/5, height*3/5)
        boardSideRDisp.rect.center = (width*4/5, height*3/5)


        #this is to rotate the complete deck at the end screen but it doesn't do it smoothly but it is fine
        self.animationCounter += 1            
        if self.animationCounter > self.animationLimitNum*5:
            completeDeckDisp.update(dt)
            self.animationCounter = self.animationLimitNum #this fixed it to be smoother
        elif self.animationCounter > self.animationLimitNum*4:
            completeDeckDisp.update(dt)
        elif self.animationCounter > self.animationLimitNum*3:
            boardSideRDisp.update(dt)
        elif self.animationCounter > self.animationLimitNum*2:
            boardGripTapeDisp.update(dt)
        elif self.animationCounter > self.animationLimitNum*1:
            boardSideLDisp.update(dt)
        elif self.animationCounter > 0:
            completeDeckDisp.update(dt)
        else:
            pass

        if not leaderboard.locked() and (playAgainButton.mouseBool == True or keys[pg.K_RETURN] == True or keys[pg.K_KP_ENTER] == True):
            #move buttons out of the screen
            playAgainButton.buttonRect.bottom = 0 
            playButton.buttonRect.bottom = 0 
            controlsButton.buttonRect.bottom = 0
            menuButton.buttonRect.bottom = 0
            objectiveButton.buttonRect.bottom = 0
            self.statsMenuRect.bottom = 0

            mainMenu.menuBool = False
            self.endBool = False
            gameActive = True
            playAgainButton.mouseBool = False
            self.dispScoreBool = False
            resetALL()

        elif menuButton.mouseBool == True:
            playButton.buttonRect.bottom = width/2 
            playAgainButton.buttonRect.bottom = 0
            controlsButton.buttonRect.bottom = height-250*0.625
            menuButton.buttonRect.bottom = 0
            controlsButton.selectBool = False
            controlsButton.mouseBool = False
            objectiveButton.selectBool = False
            objectiveButton.mouseBool = False
            self.endBool = False
            mainMenu.menuBool = True
            menuButton.mouseBool = False
            menuButton.selectBool = False
            self.dispScoreBool = False
            

        elif menuButton.mouseBool == False:
            controlsButton.buttonRect.bottom = 0
            objectiveButton.buttonRect.bottom = 0


            playAgainButton.buttonRect.center = (width/2, height/2)
            menuButton.buttonRect.center = (width/2, height/2 +200*0.625)
            self.statsMenuRect.center = (250*0.625, height-300*0.625)
            menuButton.update()

            screen.blit(mainMenu.gameNameSurf, mainMenu.mainMenuRect)
            screen.blit(self.statsMenuSurf, self.statsMenuRect)
            playAgainButton.update()

            finalSpecialCount = finalSpecialItemCount() #to get the final count of special parts

            self.specialItemCount = renderText(textFont1, f'{finalSpecialCount}/15', "black")
            self.finalCashRect = self.specialItemCount.get_rect(center = (350*0.625, height-215*0.625))
            screen.blit(self.specialItemCount, self.finalCashRect)

            screen.blit(self.endGameTextSurf, self.blinkTextRect)#(540,300))

            screen.blit(self.finalScoreText, self.finalScoreRect)
            cash.finalScore()
            leaderboard.draw(screen)
                    
class MainMenu():

    def __init__(self, imgs):
        self.playTextSurf = textFont1.render("Press Enter/Return to play!", True, 'white')

        #game Name
        # self.img = pg.image.load(resource_path("graphics/gameName5.png")).convert_alpha()
        # self.gameNameSurf = pg.transform.rotozoom(self.img, 0, 0.8*0.625)
        self.gameNameSurf = imgs[0]

        # controls menu
        # self.scalenum2 = 0.4*0.625
        # self.img2 = pg.image.load(resource_path("graphics/controlsMenu.png")).convert_alpha()
        # self.imgSize = self.img2.get_size()
        # self.imgScaled = (self.imgSize[0]*self.scalenum2, self.imgSize[1]*self.scalenum2)
        # self.controlsMenuSurf = pg.transform.smoothscale(self.img2, self.imgScaled)
        self.controlsMenuSurf = imgs[1]

        # objective menu
        # self.scalenum3 = 0.4*0.625
        # self.img3 = pg.image.load(resource_path("graphics/objectiveMenu.png")).convert_alpha()
        # self.imgSize = self.img3.get_size()
        # self.imgScaled = (self.imgSize[0]*self.scalenum3, self.imgSize[1]*self.scalenum3)
        # self.objectiveMenuSurf = pg.transform.smoothscale(self.img3, self.imgScaled) #this is better visually
        self.objectiveMenuSurf = imgs[2]

        # creating text rects
        self.mainMenuRect = pg.Surface.get_rect(self.gameNameSurf)
        self.mainMenuRect.center = (width/2, 150*0.625)

        self.controlsRect = pg.Surface.get_rect(self.controlsMenuSurf)
        self.controlsRect.center = (width/2, height/2 +100*0.625)

        self.objectiveRect = pg.Surface.get_rect(self.objectiveMenuSurf)
        self.objectiveRect.center = (width/2, height/2 +100*0.625)

        self.playTextRect = pg.Surface.get_rect(self.playTextSurf)
        self.playTextRect.center = (width/2, height*3/4)
        self.menuBool = False
        self.gameActive = False

    def update(self):
        # screen.fill(color=(255,255,255))
        if self.menuBool == True:
            sky.update()
            bgBirds.update()
            sky.draw()
            bgBirds.draw()
            world.draw()
            bgPowerLines.draw()
            screen.blit(self.gameNameSurf, self.mainMenuRect)
            
            if playButton.mouseBool == True or keys[pg.K_RETURN] == True or keys[pg.K_KP_ENTER] == True:
                #move buttons out of the screen
                playAgainButton.buttonRect.bottom = 0 
                playButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0
                menuButton.buttonRect.bottom = 0
                objectiveButton.buttonRect.bottom = 0

                self.menuBool = False
                self.gameActive = True
                playButton.mouseBool = False
                resetALL()

            elif menuButton.mouseBool == True:
                playButton.buttonRect.bottom = width/2 
                controlsButton.buttonRect.bottom = height-250*0.625
                menuButton.buttonRect.bottom = 0
                controlsButton.selectBool = False
                controlsButton.mouseBool = False
                objectiveButton.selectBool = False
                objectiveButton.mouseBool = False

                menuButton.mouseBool = False
                # print("here menu")

            elif controlsButton.selectBool == True:
                #move buttons out of the screen
                playButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0 
                objectiveButton.buttonRect.bottom = 0
                menuButton.buttonRect.center = (250*0.625, height-200*0.625)

                menuButton.update()
                screen.blit(self.controlsMenuSurf, self.controlsRect)
                touch.drawControlsHint()
                
                # self.menuBool = False
                # self.gameActive = True
                # playButton.mouseBool = False
                pass

            elif objectiveButton.selectBool == True:
                #move buttons out of the screen
                playButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0
                menuButton.buttonRect.center = (250*0.625, height-200*0.625)

                menuButton.update()
                screen.blit(self.objectiveMenuSurf, self.objectiveRect)

            elif controlsButton.mouseBool == False and objectiveButton.mouseBool == False:
                #reset positions of buttons
                playButton.buttonRect.center = (width/2, height/2)
                controlsButton.buttonRect.center = (250*0.625, height-200*0.625)
                objectiveButton.buttonRect.center = (width-250*0.625, height-200*0.625)
                menuButton.buttonRect.bottom = 0


                # playButton.reset()
                playButton.update()
                controlsButton.update()
                objectiveButton.update()

class Button():
    def __init__(self, x, y, imgSelect, sizeButton):
        self.x = x
        self.y = y
        self.imgSelect = imgSelect
        self.sizeButton = sizeButton
        # self.button_imgs = button_imgs
        self.reset()

    def reset(self):
        # self.img = [
        #     pg.image.load(resource_path("graphics/playBlueButton3.png"),
        #     pg.image.load(resource_path("graphics/controlsButton.png"),
        #     pg.image.load(resource_path("graphics/menuButtonBlue.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/menuButton.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/objectiveButton.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/playAgainButton.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/youWinButton.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/youWinButtonY.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/youWinButtonB.png")).convert_alpha()

        # ]
        # self.img = self.button_imgs
        # self.imgIndex = self.imgSelect
        # self.imgSelect = self.img[self.imgIndex]

        # scaleNum = self.sizeButton #change this to scale original image
        # self.imgSize = self.imgSelect.get_size() #(240, 300)
        # self.imgScale = (int(self.imgSize[0]*scaleNum*0.625), int(self.imgSize[1]*scaleNum*0.625))
    
        # self.button = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.button = self.imgSelect
        self.buttonRect = self.button.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.buttonRect.center = (self.x, self.y)

        self.mouseBool = False
        self.selectBool = False
        self.releasePending = False

    # def playerInput(self, event): #takes event queue input to use here
    #     #Checking mouse clicks and positions within the event Section
    #     if event.type == pg.MOUSEBUTTONUP: #captures only when it is released once
    #         # print("mouse up")
    #         if event.button == 1 and self.buttonRect.collidepoint(event.pos): #checks if mouse collides with rect
    #             # print("collide")
    #             self.mouseBool = True
    #             if self.mouseBool == True:
    #                 self.selectBool = True
    #     else:
    #         self.mouseBool = False #moved logic to the main menu
    #         pass
    def playerInput(self, event):
        # Check for mouse or touch input
        if event.type == pg.MOUSEBUTTONDOWN:  # Capture when the button is pressed
            if event.button == 1 and self.buttonRect.collidepoint(event.pos):
                self.mouseBool = True  # Button is pressed
                self.releasePending = False
        elif event.type == pg.MOUSEBUTTONUP:  # Capture when the button is released
            if event.button == 1 and self.buttonRect.collidepoint(event.pos) and self.mouseBool:
                self.selectBool = True  # Button action is confirmed
            # keep mouseBool True until the end of this frame (endFrame) so that a quick tap whose
            # press and release land in the same frame (slow computers/phones) is not lost
            self.releasePending = True

    def endFrame(self):
        if self.releasePending:
            self.mouseBool = False
            self.releasePending = False


    def draw(self):
        screen.blit(self.button, self.buttonRect)

    def update(self):
        # self.playerInput()
        self.draw()
             
class SkateParts():
    def __init__(self, skatepart_imgs, imgIndexOG, itemCount, scaleNum = 1/10, staticMotion=False):
        self.imgIndexOG = imgIndexOG
        self.itemCountOG = itemCount
        self.scaleNum = scaleNum
        self.angle = 0
        self.staticMotion = staticMotion
        
        self.reset(skatepart_imgs)

    def reset(self, skatepart_imgs):
        # self.img = [
        #     pg.image.load(resource_path("graphics/wheel.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/wheelPack.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/trucks.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/truckPack.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/bearings.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/boardDeck.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/boardSideViewL.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/boardGripTape.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/completeDeck.png")).convert_alpha(),
        #     pg.image.load(resource_path("graphics/boardSideViewR.png")).convert_alpha()

        # ]
        self.skatepart_imgs_List = skatepart_imgs
        self._rotCache = {}
        self._flipCache = {}

        self.imgIndex = self.imgIndexOG
        self.imgSelect = self.skatepart_imgs_List[self.imgIndex]

        # self.imgSize = self.imgSelect.get_size()  # Original image size
        # new_width = int(self.imgSize[0] * self.scaleNum * 0.625)
        # new_height = int(self.imgSize[1] * self.scaleNum * 0.625)
        # self.imgScale = (new_width, new_height)
    
        # self.surf = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.surf = self.imgSelect
        self.rect = self.surf.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        
        #random placement of item within range
        self.randintx = random.randint(width, width*2)
        self.randInty = random.randint(int(height*1/6), int(height*2/6))
        self.randInt = random.randint(3, 6) #in use for random x spawning

        self.rect.midtop = (self.randintx, self.randInty)
        # self.rect.center = (width/2, height/2)
    
        self.moveBool = False
        self.rotateBool = False
        self.rotateCount = 0
        self.rotateList = [0]
        self.flipCount = 0
        self.flipList = [2]
        self.flipBool = False
        self.flip_x = 0  
        self.flipTimeNum = 50      


        #count how many of the item are collected
        self.itemCount = self.itemCountOG
        # print(self.itemCount)
        self.finalItemcount = 0 #self.itemCountOG - self.itemCount
        self.spawnItem = True
        self.spawnNewTrigger = False
        self.collectSoundBool = False

    def trackItem(self):
        # self.finalItemcount = self.itemCountOG - self.itemCount
        "when ready uncomment"
        if player.readyJumpBool == True:
            self.collectSoundBool = False
        if self.staticMotion == False:

            if player.playerRect.colliderect(self.rect):
                self.rect.midbottom = (0,-50)
                
                self.itemCount -= 1
                self.finalItemcount += 1

                if self.collectSoundBool == False:
                    specialCollectSound.play()
                    # dorBailVoice.play()
                self.collectSoundBool = True #makes it so only sets loop one time
                
                
                # self.reset()
                # print(self.itemCount)
            if self.itemCount == 0:
                self.spawnItem = False
                #make item no longer spawn

            if self.imgIndexOG in self.rotateList:
                self.rotateBool = True
            elif self.imgIndexOG in self.flipList:
                self.flipBool = True
       
    def update(self, dt):
        self.trackItem()
        if self.spawnItem == True:
            if self.staticMotion == False:
                self.rect.x -= player.dx #adjust this to a global movement to remove wiggle
            
            if self.rect.right < -200:
                self.randintx = random.randint(player_xPos, width)
                self.randinty = random.randint(int(height*1/6), int(height*2/6))
                self.rect.left = width*self.randInt + self.randintx #to give more sense of randomness
                self.rect.top = self.randinty
                # self.spawnNewTrigger = True
                # print("in skateparts update:",self.randinty)

            # #later change this section to only save once the game has ended then update the endScreen()
            # self.lines = str(self.finalItemcount)
            # if gameActive == True:
            #     with open(f"saveParts{self.imgIndex}.txt", mode="w", encoding="utf-8") as f:
            #         self.lines = f.writelines(self.lines)
            
            self.draw(dt)

    def rotateItem(self, dt=0):
        self.rotateCount +=1*dt
        if self.rotateBool == True:
            if self.rotateCount >=5*dt:
                self.angle += 90 #for some reason this also makes the image change size if smaller? BUG
                self.currPosRot = self.rect.midbottom
                rotKey = self.angle % 360
                self.surf = self._rotCache.get(rotKey)
                if self.surf is None:
                    self.surf = self._rotCache[rotKey] = pg.transform.rotate(self.imgSelect, self.angle)  #rotate og image so doesn't get blurry
                # self.surf = pg.transform.smoothscale(rotatedSurf, self.imgScale)  #scale image again
                self.rect = self.surf.get_rect()
                self.rect.midbottom = self.currPosRot
                self.rotateCount = 0
    
    def flipItem(self, dt=0):
        self.flipCount +=1*dt        
        if self.flipBool == True:
            if self.flipCount >= 50*dt: #self.flipTimeNum*2: #50 may need to change
                self.flip_x = 1
                self.flipCount = 0
            elif self.flipCount >= 25*dt: #self.flipTimeNum:
                self.flip_x = 0    
            self.currPosRot = self.rect.midbottom
            self.surf = self._flipCache.get(self.flip_x)
            if self.surf is None:
                self.surf = self._flipCache[self.flip_x] = pg.transform.flip(self.imgSelect, self.flip_x, 0)
            # self.surf = pg.transform.smoothscale(rotatedSurf, self.imgScale)  #scale image again
            self.rect = self.surf.get_rect()
            self.rect.midbottom = self.currPosRot                         

    def draw(self, dt):
        if self.rotateBool == True:
            self.rotateItem(dt)
        elif self.flipBool == True:
            self.flipItem(dt)
        screen.blit(self.surf, self.rect)
        # pg.draw.rect(surface=screen, color="red", rect=self.rect, width= 2)

class Cash():
    def __init__(self, img, staticMove = False):
        self.staticMove = staticMove
        self.img = img
        self.reset()

    def reset(self):
        # self.imgOG = pg.image.load(resource_path("graphics/cash.png")).convert_alpha()

        self.x = width*1/2
        self.y = height*2/3
        
        # self.width = self.imgOG.get_width()
        # self.height = self.imgOG.get_height()

        # self.scaleNum = 1/10

        # self.newWidth = int(self.width *  self.scaleNum * 0.625)
        # self.newHeight = int(self.height * self.scaleNum * 0.625) #no floats
        # self.imgScale = (self.newWidth, self.newHeight)

        # self.img = pg.transform.smoothscale(self.imgOG, self.imgScale)        

        self.rect = self.img.get_rect()
        self.rect.midbottom = (self.x, self.y)

        self.count = 0
        self.angle = 0
        self.rstBool = False
        self.cashcount = 0
    
    def draw(self):
        # self.img = pg.transform.rotozoom(self.img, self.angle, 1)
        # self.rect = self.img.get_rect()

        # self.count += 1
        # if self.count == 20:      
        #     self.angle += 45
        #     self.count = 0

        # pg.draw.rect(surface=screen, color="red", rect=self.rect, width=2)
        screen.blit(self.img, self.rect)

    def finalScore(self):
        # if gameActive == False:
        # with open("saveCash.txt", mode="r", encoding="utf-8") as f:
        #     self.cashScore = f.readlines()
        #     self.finalCash = self.cashScore[0].strip()
    
        # self.finalCashText = textFont1.render(f'Cash Collected: ${self.finalCash}', True, ("green"))
        self.finalCashText = renderText(textFont1, f'${self.cashcount}', "green")
        self.finalCashRect = self.finalCashText.get_rect(center = (350*0.625, height-260*0.625))
        screen.blit(self.finalCashText, self.finalCashRect)
    
    def rerollPosition(self):
        self.randintx = random.randint(int(player_xPos), int(width))
        self.randinty = random.randint(int(height*2/4), int(height*2/3))

    def update(self):
        if self.staticMove == False:
            self.rect.x -= player.dx

            if self.rect.colliderect(player.playerRect.x +player.dx, player.playerRect.y, player.playerRect.w, player.playerRect.h): #add prediction collision with dx
                self.rerollPosition()
                cashSound.play() #delay in sound, clip audio
                self.rect.left = width + self.randintx
                self.rect.bottom = self.randinty
                self.cashcount += 1 #add a cash count and load to text after some amount
            if self.rect.right < 0:
                self.rerollPosition()
                self.rect.left = width + self.randintx
                self.rect.bottom = self.randinty
        self.draw()
        
class SpecialItemDisp():
    def __init__(self, img, specialItemList = None):
        # spawnSpecialItemList
        self.conStartPosx = 0
        self.conStartPosy = 0
        self.winButtonAnimationCounter = 0
        self.animationLimitNum = 50

        # self.imgConfetti = pg.image.load(resource_path("graphics/winConfetti.png")).convert_alpha()
        # self.scaleNum = 1/2
        # self.imgConfettiWidth = self.imgConfetti.get_width()
        # self.imgConfettiHeight = self.imgConfetti.get_height()
        # self.scaledimg = (self.imgConfettiWidth*0.625, self.imgConfettiHeight*0.625)
        # self.imgConfetti = pg.transform.smoothscale(self.imgConfetti, self.scaledimg)
        self.imgConfetti = img

        self.imgRect = self.imgConfetti.get_rect()
        self.reset()

    def reset(self):
        cashDisp.rect.center = (width*1/6, 100 *0.625)
        wheelPack.rect.center = (width*2/6, 100 *0.625)
        truckPack.rect.center = (width*3/6, 100 *0.625)
        bearingsDisp.rect.center = (width*4/6, 100 *0.625)
        boardDeckDisp.rect.center = (width*5/6, 100 *0.625)

        self.cashCount = renderText(textFont1, f': ${cash.cashcount}', "black")
        self.cashCountRect = self.cashCount.get_rect(center = (int(width*1/6 +80*0.625), 100 *0.625))

        self.wheelCount = renderText(textFont1, f': {wheel.finalItemcount}/4', "black")
        self.wheelCountRect = self.wheelCount.get_rect(center = (width*2/6 +80 *0.625, 100 *0.625))

        self.truckCount = renderText(textFont1, f': {trucks.finalItemcount}/2', "black")
        self.truckCountRect = self.truckCount.get_rect(center = (width*3/6 +80 *0.625, 100 *0.625))

        self.bearingCount = renderText(textFont1, f': {bearings.finalItemcount}/8', "black")
        self.bearingCountRect = self.bearingCount.get_rect(center = (width*4/6 +80 *0.625, 100 *0.625))

        self.boardDeckCount = renderText(textFont1, f': {boardDeck.finalItemcount}/1', "black")
        self.boardCountRect = self.boardDeckCount.get_rect(center = (width*5/6 +80 *0.625, 100 *0.625))

        self.winTextSurf = renderText(textFont1, 'You Win!!!', "green")
        self.winTextRect = self.winTextSurf.get_rect(center = (width/2 , 200 *0.625))

    def drawConfetti(self, dt):
        self.conStartPosy += 63*dt
        if self.conStartPosy >= self.imgConfetti.get_height(): #-int(300*0.625):
            self.conStartPosy = 0
        screen.blit(self.imgConfetti, (self.conStartPosx , self.conStartPosy, self.imgRect.w, self.imgRect.h))
        screen.blit(self.imgConfetti, (self.conStartPosx , self.conStartPosy- self.imgConfetti.get_height())) #+int(300*0.625)))

    def update(self, dt):     
        wheelPack.update(dt)
        truckPack.update(dt)
        bearingsDisp.update(dt)
        boardDeckDisp.update(dt)
        cashDisp.update()

        screen.blit(self.wheelCount, self.wheelCountRect)
        screen.blit(self.truckCount, self.truckCountRect)
        screen.blit(self.bearingCount, self.bearingCountRect)
        screen.blit(self.boardDeckCount, self.boardCountRect)
        screen.blit(self.cashCount, self.cashCountRect)

        #if win condition is met
        if completeDeck.itemCount == 0:
            youWinButton.update()
            self.drawConfetti(dt)
        if player.playerRect.collidelist(rectsCollideList):
            self.reset()

#timers and ticks
start_ticks = pg.time.get_ticks()

#Score
def displayScore():
    global currentTime, cT
    cT = (pg.time.get_ticks() - start_ticks)
    currentTime = int((cT)/1000)
    scoreSurf = renderText(textFont1, f'Time: {currentTime}s', (255,255,255))
    scoreRect = scoreSurf.get_rect(topleft = (10, 10))
    lines = str(currentTime)


    if gameActive == True:
        screen.blit(scoreSurf, scoreRect)

    return lines

def resetALL():
    #RESETTING CHARACTER POSITIONS AND ITERERATIONS:
    global start_ticks, current_ticks
    start_ticks = pg.time.get_ticks()
    current_ticks = 0
    # player.playerRect.x  = player_xPos
    # player.readyJumpBool = False
    # player.dx = 0
    obstacle1.ObstacleRect.x = width
    # NPC1.NPC1Rect.x = width #uncomment
    mainMenu.menuBool = False
    player.bailBool = False
    endScreen.saveBool = False


    #To reset all counts and spawn bools related to special items
    "using this instead of reset cause was slowing down the game"
    wheel.finalItemcount = 0
    wheel.itemCount = wheel.itemCountOG
    wheel.spawnItem = True

    trucks.finalItemcount = 0
    trucks.itemCount = trucks.itemCountOG
    trucks.spawnItem = True

    bearings.finalItemcount = 0
    bearings.itemCount = bearings.itemCountOG
    bearings.spawnItem = True

    boardDeck.finalItemcount = 0
    boardDeck.itemCount = boardDeck.itemCountOG
    boardDeck.spawnItem = True

    completeDeck.finalItemcount = 0
    completeDeck.itemCount = completeDeck.itemCountOG
    completeDeck.spawnItem = True

    # gameActive = True
    # sky.reset()
    # world.reset()
    player.reset(player_xPos,player_yPos)
    cash.reset()

#---------------------------------------

#INSTANTIATING CLASSES:
sky = World(bg_List[0], 0.25, BG_Y[0])
world = World(bg_List[1],0, BG_Y[1])
bgPowerLines = World(bg_List[2],0, BG_Y[2])
bgBirds = World(bg_List[3],0.55, BG_Y[3])

player = Player(player_xPos, player_yPos)
nPC = NPC((width-400*0.625),524*0.625)
endScreen = EndScreen(statsMenuImg)
mainMenu = MainMenu(mainMenuImgs)

playButton = Button(width/2, height/2, button_imgs[0], (1/6))

playAgainButton = Button(width/2, height/2, button_imgs[4], (1/3))
controlsButton = Button(250, height-200, button_imgs[1], (1/4))
menuButton = Button(250, height-200, button_imgs[2], (1/6))
objectiveButton = Button(width-250, height-200, button_imgs[3], (1/4))
youWinButton = Button(width/2, int(200*0.625), button_imgs[5], (1/4))
# youWinButtonY = Button(width/2, int(200*0.625), button_imgs[7], (1/4))
# youWinButtonB = Button(width/2, int(200*0.625), button_imgs[8], (1/4))

# (the old prototype jumpButton was replaced by the TouchControls overlay below)

obstacle1 = Obstacles(width/2, player_yPos)
cash = Cash(cashImg)
cashDisp = Cash(cashImg, True)

# #skateparts
wheel = SkateParts(skatepart_imgs, 0, 4)
wheelPack = SkateParts(skatepart_imgs, 1, 1, 1/18, True)
trucks = SkateParts(skatepart_imgs, 2, 2) 
truckPack = SkateParts(skatepart_imgs, 3,1, 1/18, True)
bearings = SkateParts(skatepart_imgs, 4, 8)
bearingsDisp = SkateParts(skatepart_imgs, 10, 1, 1/18, True)
boardDeck = SkateParts(skatepart_imgs, 5, 1, 1/14)
boardDeckDisp = SkateParts(skatepart_imgs, 11, 1, 1/18, True)
boardSideLDisp = SkateParts(skatepart_imgs, 6, 1, 1/8, True)
boardSideRDisp = SkateParts(skatepart_imgs, 9, 1, 1/8, True)
boardGripTapeDisp = SkateParts(skatepart_imgs, 7, 1, 1/8, True)
completeDeckDisp = SkateParts(skatepart_imgs, 8, 1, 1/8, True)
completeDeck = SkateParts(skatepart_imgs, 8, 1)


specialItemSpawnCounter = 0 #used to make a timer to spawn them more sparely
spawnSpecialItemBool = True
spawnSpecialItemList = [wheel,
                        trucks,
                        bearings,
                        boardDeck
                        ]

rectsCollideList = [
    wheel.rect,
    trucks.rect,
    bearings.rect,
    boardDeck.rect,
    cash.rect
]


# #to display tracking during game on screen
specialItemDisp = SpecialItemDisp(imgConfetti, spawnSpecialItemList )

def finalSpecialItemCount():
    itemCountList = [wheel.finalItemcount,
                    trucks.finalItemcount,
                    bearings.finalItemcount,
                    boardDeck.finalItemcount
                    # completeDeck.finalItemcount

                    ]
    finalSpecialItemCount = sum(itemCountList)
    return finalSpecialItemCount

def totalSpecialPartsList():
    itemCountList = [wheel.itemCountOG,
                    trucks.itemCountOG,
                    bearings.itemCountOG,
                    boardDeck.itemCountOG
                    # completeDeck.itemCountOG

                    ]
    partsList = sum(itemCountList)
    return partsList



# ---------------------------------------------------------------------------
# TOUCH CONTROLS (phones / tablets)
# ---------------------------------------------------------------------------
# The game has four inputs, which on a touch screen become TWO "slide pads", one per thumb:
#
#     LEFT PAD   top = BRAKE (a key)       bottom = PUSH (d key)
#     RIGHT PAD  top = GRIND (shift key)   bottom = JUMP (space key)
#
# A finger that lands on a pad stays attached to it until it lifts, even if it slides off the
# edge, and the zone it is over is worked out from where it is. So you can hold PUSH and slide up
# to BRAKE (and back) without letting go.
# On the right pad GRIND latches: once your thumb has touched the GRIND zone it stays engaged
# until you lift your thumb, so you can slide down to JUMP and ollie off the rail while still
# grinding. After you lift, GRIND stays "armed" for a short grace time (GRIND_GRACE_TICKS) and, if
# you land on an obstacle in that time, stays engaged until you leave the obstacle. So a quick tap
# before a rail works too, and if you don't land on anything the tap simply times out.
# Keyboard players never see any of this.
GRIND_GRACE_TICKS = 9           # 9 ticks = 0.15 s (set to 0 for strictly hold-to-grind)
GRIND_SLIDE_TICKS = 8           # sliding from GRIND down to JUMP: grind switches off after this many ticks (0.13 s)
PORTRAIT_MIN_EXTRA = 380        # least extra height (game pixels) under the zoomed game in portrait
PORTRAIT_MAX_H = 1500           # tallest window we will ask for (keeps phones fast)
PORTRAIT_ZOOM = 1.25            # upright phone: the game is shown this much bigger (1.0 = no zoom)
ZOOM_W = int(round(width / PORTRAIT_ZOOM))      # part of the world (from the left) that is shown: 640 px of 800
ZOOM_H = int(round(height * PORTRAIT_ZOOM))     # ... blown up to this height: 562 px
HUD_H = 250                     # height of the collectibles/score layer that is NOT zoomed
BAR_ASPECT_MIN = 1.95           # landscape phones at least this wide (width/height) get side bars
BAR_MIN, BAR_MAX = 100, 170     # side bar width limits in game pixels
PANEL_COLOR = (22, 24, 32)
BAR_COLOR = (10, 10, 14)

try:
    import platform as _platform   # under pygbag this one has .window (the browser)
except Exception:
    _platform = None

def browserViewport():
    """(w, h) of the web page the game is in, or None when not running in a browser."""
    try:
        w = float(_platform.window.innerWidth)
        h = float(_platform.window.innerHeight)
        if w > 0 and h > 0:
            return w, h
    except Exception:
        pass
    return None

def isTouchDevice():
    try:
        return int(_platform.window.navigator.maxTouchPoints) > 0
    except Exception:
        return False

def wantedLayout(touchDevice):
    """(window width, window height, side bar width) for the page we are in.
    - normal / desktop / no browser:        800 x 450, no bars
    - phone upright:                        800 x taller (zoomed game on top, control box underneath)
    - phone sideways and wide (>= 1.95):    wider window, the game in the middle, a bar each side for the pads
    - everything else sideways (iPad etc.): 800 x 450, see-through pads on top of the game"""
    vp = browserViewport()
    if vp is None or not touchDevice:
        return width, height, 0
    vw, vh = vp
    if vh > vw:
        h = int(max(ZOOM_H + PORTRAIT_MIN_EXTRA, min(PORTRAIT_MAX_H, width * vh / vw)))
        return width, h, 0
    aspect = vw / vh
    if aspect >= BAR_ASPECT_MIN:
        bw = int(max(BAR_MIN, min(BAR_MAX, round((aspect * height - width) / 2))))
        return width + 2 * bw, height, bw
    return width, height, 0


# ---------------------------------------------------------------------------
# JAVASCRIPT BRIDGE (only does something in the browser; every call is wrapped in try/except)
# ---------------------------------------------------------------------------
def jsEval(code, default=""):
    try:
        r = _platform.window.eval(code)
        return default if r is None else r
    except Exception:
        return default


# ---------------------------------------------------------------------------
# ARCADE LEADERBOARD  (top 3 on the end screen, 3-letter initials)
# ---------------------------------------------------------------------------
# Score = seconds survived (higher is better).
# Where it is kept:
#   1. in the browser's localStorage (so each phone/computer remembers its own scores) and, when the
#      game runs as normal Python on a computer, in a file called leaderboard.json next to main.py;
#   2. optionally ALSO on a shared board for everybody, if you fill in LEADERBOARD_URL below with
#      the address of the Google Apps Script from leaderboard_server.gs (see the README). Every
#      finished run is then added as a row (time, initials, score, device id) to your Google Sheet,
#      which is the "file of who has played".
# The first time someone finishes a run they are asked for initials; after that they are only asked
# when the run makes the top 3 (their last initials are pre-filled). Other runs are logged silently.
LEADERBOARD_URL = ""            # e.g. "https://script.google.com/macros/s/XXXX/exec"  ("" = this device only)
LB_KEY = "skaterKittyBoard2"
LB_FILE = "leaderboard.json"
LB_MAX_PLAYS = 100              # how many past runs the local log keeps
LB_MAX_SCORE = 9999             # anything above this is treated as a mistake / cheat
# Score (points) = seconds survived + CASH_POINTS per dollar + PART_POINTS per skate part, so just
# letting the timer run is not enough to win. Change these to re-balance.
CASH_POINTS = 5
PART_POINTS = 20
# The board starts with these three so it is easy to get on it (30 s, 1 min, 2 min worth of points).
DEFAULT_TOP = [{"n": "VMR", "s": 120}, {"n": "CAT", "s": 60}, {"n": "KIT", "s": 30}]


def cleanName(s):
    s = "".join(ch for ch in str(s).upper() if "A" <= ch <= "Z")[:3]
    return s


class Leaderboard():
    def __init__(self):
        self.data = {"top": [dict(e) for e in DEFAULT_TOP], "last": "", "plays": [], "id": ""}
        self.lastPoints = None
        self.detail = ""
        self.remote = None            # top list from the shared board (None = not loaded)
        self.entering = False         # the initials pop-up is open
        self.letters = ["A", "A", "A"]
        self.cursor = 0
        self.pending = 0              # the score being entered
        self.qualified = False
        self.waitRelease = False
        self.hl = None                # (name, score) of this run, shown highlighted
        self.refetchAt = 0
        self.load()
        if not self.data["id"]:
            self.data["id"] = "".join(random.choice("abcdefghijkmnpqrstuvwxyz23456789") for _ in range(10))
        self.buildUI()
        self.fetchRemote()

    # ---------------- storage ----------------
    def load(self):
        raw = jsEval("(function(){try{return localStorage.getItem(%s)||''}catch(e){return ''}})()" % json.dumps(LB_KEY))
        raw = str(raw) if raw else ""
        if not raw:
            try:
                with open(LB_FILE, encoding="utf-8") as f:
                    raw = f.read()
            except Exception:
                raw = ""
        try:
            d = json.loads(raw)
            top = [{"n": cleanName(e["n"]), "s": int(e["s"])} for e in d.get("top", [])][:10]
            plays = d.get("plays", [])[-LB_MAX_PLAYS:]
            self.data = {"top": top, "last": cleanName(d.get("last", "")), "plays": plays, "id": str(d.get("id", ""))[:16]}
        except Exception:
            pass

    def save(self):
        s = json.dumps(self.data)
        jsEval("(function(){try{localStorage.setItem(%s,%s)}catch(e){}})()" % (json.dumps(LB_KEY), json.dumps(s)))
        try:
            with open(LB_FILE, "w", encoding="utf-8") as f:
                f.write(s)
        except Exception:
            pass

    def top3(self):
        rows = list(self.data["top"])
        if self.remote:
            rows = list(self.remote) + [dict(e) for e in DEFAULT_TOP]
        return sorted(rows, key=lambda e: -e["s"])[:3]

    def qualifies(self, score):
        top = self.top3()
        return score > 0 and (len(top) < 3 or score > top[-1]["s"])

    def record(self, name, score):
        name = cleanName(name) or "???"
        self.data["plays"].append({"n": name, "s": score, "t": int(time.time())})
        self.data["plays"] = self.data["plays"][-LB_MAX_PLAYS:]
        self.data["top"].append({"n": name, "s": score})
        self.data["top"] = sorted(self.data["top"], key=lambda e: -e["s"])[:10]
        self.hl = (name, score)
        self.save()
        self.submitRemote(name, score)

    # ---------------- shared board (optional) ----------------
    def jsFetch(self, query):
        if not LEADERBOARD_URL:
            return
        url = json.dumps(LEADERBOARD_URL + "?" + query)
        jsEval("(function(){try{fetch(%s+'&_='+Date.now()).then(function(r){return r.text()})"
               ".then(function(t){window.__skLB=t}).catch(function(e){})}catch(e){}})()" % url)

    def fetchRemote(self):
        self.jsFetch("action=top&n=3")

    def submitRemote(self, name, score):
        self.jsFetch("action=submit&name=%s&score=%d&id=%s" % (name, score, self.data["id"]))
        self.refetchAt = pg.time.get_ticks() + 2500

    def pollRemote(self):
        if not LEADERBOARD_URL:
            return
        raw = str(jsEval("window.__skLB||''"))
        if raw:
            try:
                rows = json.loads(raw).get("top", [])
                self.remote = [{"n": cleanName(e["n"]), "s": int(e["s"])} for e in rows][:3]
            except Exception:
                pass
        if self.refetchAt and pg.time.get_ticks() >= self.refetchAt:
            self.refetchAt = 0
            self.fetchRemote()

    # ---------------- the run ended ----------------
    def onRunEnd(self, scoreStr, cashCount=0, partCount=0):
        try:
            secs = int(scoreStr)
            score = max(0, min(LB_MAX_SCORE, secs + CASH_POINTS * int(cashCount) + PART_POINTS * int(partCount)))
        except Exception:
            return
        self.lastPoints = score
        self.detail = "%ds + $%d + %d parts" % (secs, int(cashCount), int(partCount))
        self.hl = None
        self.pending = score
        if score <= 0:
            return
        self.qualified = self.qualifies(score)
        if self.qualified or not self.data["last"]:
            self.openEntry()
        else:
            self.record(self.data["last"], score)     # quietly keep the log

    def openEntry(self):
        last = self.data["last"]
        self.letters = list(last) if len(last) == 3 else ["A", "A", "A"]
        self.cursor = 0
        self.entering = True
        for b in menuButtons:          # a tap that was already on its way must not press a button
            b.mouseBool = False
            b.selectBool = False
            b.releasePending = False

    def cancel(self):
        self.entering = False
        self.waitRelease = False

    def confirm(self):
        name = "".join(self.letters)
        self.data["last"] = name
        self.record(name, self.pending)
        self.entering = False
        self.waitRelease = True        # the Enter that confirmed must not also restart the game

    def locked(self):
        """True while the pop-up is open (and until Enter is let go afterwards)."""
        if self.entering:
            return True
        if self.waitRelease:
            if keys.real[pg.K_RETURN] or keys.real[pg.K_KP_ENTER]:
                return True
            self.waitRelease = False
        return False

    # ---------------- input (only while the pop-up is open) ----------------
    def handleEvent(self, event, gameEv, asMouse):
        if event.type == pg.KEYDOWN:
            k = event.key
            if k in (pg.K_RETURN, pg.K_KP_ENTER):
                self.confirm()
            elif k == pg.K_ESCAPE:
                self.entering = False            # skip: nothing is saved for this run
            elif k == pg.K_BACKSPACE or k == pg.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
            elif k == pg.K_RIGHT or k == pg.K_TAB:
                self.cursor = min(2, self.cursor + 1)
            elif k == pg.K_UP:
                self.step(self.cursor, 1)
            elif k == pg.K_DOWN:
                self.step(self.cursor, -1)
            else:
                ch = getattr(event, "unicode", "")
                if len(ch) == 1 and "a" <= ch.lower() <= "z":
                    self.letters[self.cursor] = ch.upper()
                    self.cursor = min(2, self.cursor + 1)
            return
        ev = asMouse if asMouse is not None else gameEv
        if ev.type == pg.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 1:
            if asMouse is None and getattr(ev, "touch", False) and touch.fingerSeen:
                return                           # the finger event already did this tap
            self.click(ev.pos)

    def step(self, i, d):
        self.letters[i] = chr((ord(self.letters[i]) - 65 + d) % 26 + 65)

    def click(self, pos):
        for i in range(3):
            if self.upRects[i].collidepoint(pos):
                self.cursor = i
                self.step(i, 1)
                return
            if self.downRects[i].collidepoint(pos):
                self.cursor = i
                self.step(i, -1)
                return
            if self.boxRects[i].collidepoint(pos):
                self.cursor = i
                return
        if self.okRect.collidepoint(pos):
            self.confirm()
        elif self.skipRect.collidepoint(pos):
            self.entering = False

    # ---------------- drawing ----------------
    def buildUI(self):
        self.fontRow = pg.font.Font(None, 22)
        self.fontHead = pg.font.Font(None, 22)
        self.fontBig = pg.font.Font(None, 68)
        self.fontMid = pg.font.Font(None, 30)
        self.fontSmall = pg.font.Font(None, 21)
        # the small top-3 panel on the end screen
        self.boardRect = pg.rect.Rect(615, 112, 177, 94)
        bg = pg.Surface(self.boardRect.size, pg.SRCALPHA)
        pg.draw.rect(bg, (8, 10, 22, 205), (0, 0) + self.boardRect.size, 0, border_radius=10)
        pg.draw.rect(bg, (255, 215, 0, 230), (0, 0) + self.boardRect.size, 2, border_radius=10)
        self.boardBG = bg.convert_alpha()
        # the initials pop-up
        self.popRect = pg.rect.Rect(0, 0, 400, 330)
        self.popRect.center = (width // 2, height // 2)
        pop = pg.Surface(self.popRect.size, pg.SRCALPHA)
        pg.draw.rect(pop, (8, 10, 22, 240), (0, 0) + self.popRect.size, 0, border_radius=16)
        pg.draw.rect(pop, (255, 215, 0, 255), (0, 0) + self.popRect.size, 3, border_radius=16)
        self.popBG = pop.convert_alpha()
        cx = width // 2
        self.boxRects, self.upRects, self.downRects = [], [], []
        for i in range(3):
            x = cx + (i - 1) * 90
            self.boxRects.append(pg.rect.Rect(x - 35, 170, 70, 70))
            self.upRects.append(pg.rect.Rect(x - 36, 125, 72, 45))
            self.downRects.append(pg.rect.Rect(x - 36, 240, 72, 45))
        self.okRect = pg.rect.Rect(0, 0, 150, 46)
        self.okRect.center = (cx, 330)
        self.skipRect = pg.rect.Rect(0, 0, 110, 30)
        self.skipRect.center = (cx, 372)

    def draw(self, surf):
        r = self.boardRect
        surf.blit(self.boardBG, r.topleft)
        head = renderText(self.fontHead, "TOP 3 (POINTS)", (255, 215, 0))
        surf.blit(head, head.get_rect(center=(r.centerx, r.y + 14)))
        colors = [(255, 215, 0), (215, 215, 225), (205, 127, 50)]
        rows = self.top3()
        hlDone = False
        for i in range(3):
            y = r.y + 31 + i * 20
            if i < len(rows):
                e = rows[i]
                mine = (not hlDone) and self.hl is not None and (e["n"], e["s"]) == self.hl
                hlDone = hlDone or mine
                col = (121, 224, 48) if mine else colors[i]
                rank, name, score = str(i + 1), e["n"], "%d" % e["s"]
            else:
                col = (110, 110, 125)
                rank, name, score = str(i + 1), "---", "--"
            t1 = renderText(self.fontRow, rank, col)
            t2 = renderText(self.fontRow, name, col)
            t3 = renderText(self.fontRow, score, col)
            surf.blit(t1, (r.x + 14, y))
            surf.blit(t2, (r.x + 40, y))
            surf.blit(t3, (r.right - 14 - t3.get_width(), y))
        if self.lastPoints is not None:
            t = renderText(self.fontRow, "Your score: %d pts  (%s)" % (self.lastPoints, self.detail), (255, 255, 255))
            surf.blit(t, t.get_rect(center=(width // 2, 186)))
        if self.entering:
            self.drawEntry(surf)

    def drawEntry(self, surf):
        p = self.popRect
        surf.blit(self.popBG, p.topleft)
        cx = p.centerx
        title = "NEW HIGH SCORE!" if self.qualified else "ENTER YOUR INITIALS"
        t = renderText(self.fontMid, title, (255, 215, 0))
        surf.blit(t, t.get_rect(center=(cx, 82)))
        t = renderText(self.fontRow, "%d points  (%s)" % (self.pending, self.detail), (255, 255, 255))
        surf.blit(t, t.get_rect(center=(cx, 106)))
        blinkOn = (pg.time.get_ticks() // 350) % 2 == 0
        for i in range(3):
            box = self.boxRects[i]
            sel = (i == self.cursor)
            pg.draw.rect(surf, (30, 34, 60), box, 0, border_radius=10)
            pg.draw.rect(surf, (255, 215, 0) if (sel and blinkOn) else (120, 125, 150), box, 3, border_radius=10)
            ch = renderText(self.fontBig, self.letters[i], (255, 255, 255))
            surf.blit(ch, ch.get_rect(center=box.center))
            u, d = self.upRects[i], self.downRects[i]
            pg.draw.polygon(surf, (121, 224, 48), [(u.centerx, u.y + 8), (u.centerx - 18, u.bottom - 8), (u.centerx + 18, u.bottom - 8)])
            pg.draw.polygon(surf, (121, 224, 48), [(d.centerx, d.bottom - 8), (d.centerx - 18, d.y + 8), (d.centerx + 18, d.y + 8)])
        t = renderText(self.fontSmall, "Tap the arrows or type your initials", (170, 175, 195))
        surf.blit(t, t.get_rect(center=(cx, 297)))
        pg.draw.rect(surf, (121, 224, 48), self.okRect, 0, border_radius=12)
        t = renderText(self.fontMid, "OK", (10, 20, 10))
        surf.blit(t, t.get_rect(center=self.okRect.center))
        t = renderText(self.fontSmall, "skip", (170, 175, 195))
        surf.blit(t, t.get_rect(center=self.skipRect.center))


class SlidePad():
    """A rounded pad with a top zone and a bottom zone."""
    def __init__(self, topLabel, bottomLabel, topColor, bottomColor):
        self.topLabel, self.bottomLabel = topLabel, bottomLabel
        self.topColor, self.bottomColor = topColor, bottomColor
        self.rect = pg.rect.Rect(0, 0, 10, 10)
        self.splitY = 0
        self.slop = 18
        self.parts = []   # (pos, surface off, surface on) for top and bottom zone

    def build(self, rect, topFrac, solid, font, slop):
        self.rect = pg.rect.Rect(rect)
        self.slop = slop
        topH = int(self.rect.h * topFrac)
        self.splitY = self.rect.y + topH
        gap = 6
        self.parts = []
        zones = [
            (self.rect.y, topH - gap // 2, self.topLabel, self.topColor),
            (self.splitY + gap // 2, self.rect.bottom - self.splitY - gap // 2, self.bottomLabel, self.bottomColor),
        ]
        for y, h, label, color in zones:
            off = self.makeSurf(self.rect.w, h, label, color, False, solid, font)
            on = self.makeSurf(self.rect.w, h, label, color, True, solid, font)
            self.parts.append(((self.rect.x, y), off, on))

    def makeSurf(self, w, h, label, color, on, solid, font):
        surf = pg.Surface((w, h), pg.SRCALPHA)
        if solid:      # portrait panel: opaque (fast), idle zones are a dark version of the colour
            c = color if on else (int(color[0]*0.42), int(color[1]*0.42), int(color[2]*0.42))
            fill = (c[0], c[1], c[2], 255)
        else:          # landscape: see-through over the game, like the old round buttons
            fill = (color[0], color[1], color[2], 235 if on else 120)
        radius = min(w, h) // 3
        pg.draw.rect(surf, fill, (0, 0, w, h), 0, border_radius=radius)
        pg.draw.rect(surf, (255, 255, 255, 230 if on else 150), (0, 0, w, h), 3, border_radius=radius)
        text = font.render(label, True, (255, 255, 255))
        surf.blit(text, text.get_rect(center=(w // 2, h // 2)))
        return surf.convert_alpha()   # keeps the rounded corners clean

    def hit(self, x, y):
        s = self.slop
        return self.rect.x - s <= x <= self.rect.right + s and self.rect.y - s <= y <= self.rect.bottom + s

    def zone(self, y):
        return "top" if y < self.splitY else "bottom"

    def draw(self, surface, topOn, bottomOn):
        (p0, off0, on0), (p1, off1, on1) = self.parts
        surface.blit(on0 if topOn else off0, p0)
        surface.blit(on1 if bottomOn else off1, p1)


class TouchControls():
    def __init__(self):
        self.active = False        # True after the first touch (landscape: pads only show then)
        self.fingerSeen = False    # True once real finger events arrive
        self.fingers = {}          # finger id -> {"pad", "zone", "latched", "seen"}
        self.state = {"push": False, "brake": False, "jump": False, "grind": False}
        self.jumpPulse = False     # a tap so quick that no frame saw it still counts as a jump
        self.grindHeld = False
        self.armTicks = 0
        self.engaged = False
        self.lastGrind = False
        self.portrait = False
        self.mode = "overlay"      # overlay (pads on the game) | bars (landscape side bars) | portrait
        self.smallFont = pg.font.Font(None, 26)
        self.bigFont = pg.font.Font(None, 46)
        self.left = SlidePad("BRAKE", "PUSH", (150, 150, 150), (121, 224, 48))
        self.right = SlidePad("GRIND", "JUMP", (224, 48, 74), (48, 157, 224))
        self.pads = [self.left, self.right]
        self.hint = renderText(textFont2, "Touch screen:  left pad = BRAKE / PUSH     right pad = GRIND / JUMP     (slide between them)", "white")
        self.hintRect = self.hint.get_rect(center=(width/2, height-18))
        self.panelHint = renderText(textFont2, "Slide your thumb between the zones", (200, 200, 210))
        self.setLayout(width, height, 0)

    def setLayout(self, dispW, dispH, barW=0):
        self.dispW, self.dispH = dispW, dispH
        self.portrait = dispH > height
        self.mode = "portrait" if self.portrait else ("bars" if barW else "overlay")
        if self.mode == "overlay":
            # on top of the game, bottom corners (where the old round buttons were)
            y = height - 228
            self.left.build((14, y, 112, 199), 0.38, False, self.smallFont, 18)
            self.right.build((width - 14 - 112, y, 112, 199), 0.38, False, self.smallFont, 18)
        elif self.mode == "bars":
            # tall solid pads inside the black bars on either side of the game
            self.barRects = [pg.rect.Rect(0, 0, barW, height), pg.rect.Rect(dispW - barW, 0, barW, height)]
            self.left.build((10, 50, barW - 20, height - 86), 0.38, True, self.smallFont, 14)
            self.right.build((dispW - barW + 10, 50, barW - 20, height - 86), 0.38, True, self.smallFont, 14)
        else:
            # in the black box under the zoomed game
            area = dispH - ZOOM_H
            padH = min(640, area - 140)
            y = dispH - 70 - padH
            self.left.build((60, y, 250, padH), 0.36, True, self.bigFont, 30)
            self.right.build((width - 60 - 250, y, 250, padH), 0.36, True, self.bigFont, 30)
            self.panelHintRect = self.panelHint.get_rect(center=(width/2, ZOOM_H + 90))
        self.fingers.clear()

    # ---------------- input ----------------
    def handleEvent(self, event):
        t = event.type
        if t == pg.FINGERDOWN or t == pg.FINGERMOTION:
            self.active = True
            self.fingerSeen = True
            self.pointerMove(event.finger_id, event.x*self.dispW, event.y*self.dispH)
        elif t == pg.FINGERUP:
            self.pointerUp(event.finger_id)
        elif getattr(event, "touch", False) and not self.fingerSeen:
            # fallback: some browsers only deliver touches as (touch-flagged) mouse events
            if t == pg.MOUSEBUTTONDOWN or (t == pg.MOUSEMOTION and "mouse" in self.fingers):
                self.active = True
                self.pointerMove("mouse", event.pos[0], event.pos[1])
            elif t == pg.MOUSEBUTTONUP:
                self.pointerUp("mouse")
        elif t == getattr(pg, "WINDOWFOCUSLOST", -1):
            self.fingers.clear()    # don't leave a zone stuck down if the page loses focus
            self.armTicks = 0

    def pointerMove(self, pid, x, y):
        rec = self.fingers.get(pid)
        if rec is None:
            rec = self.fingers[pid] = {"pad": None, "zone": "top", "latched": False, "seen": False}
        if rec["pad"] is None:          # a finger attaches to the first pad it touches
            for pad in self.pads:
                if pad.hit(x, y):
                    rec["pad"] = pad
                    break
        pad = rec["pad"]
        if pad is not None:
            rec["zone"] = pad.zone(y)
            if pad is self.right and rec["zone"] == "top":
                rec["latched"] = True                  # GRIND stays on while the thumb is on it ...
                rec["slide"] = GRIND_SLIDE_TICKS       # ... and for a moment after it slides down to JUMP
                self.armTicks = GRIND_GRACE_TICKS      # (a tap shorter than one frame still counts)

    def pointerUp(self, pid):
        rec = self.fingers.pop(pid, None)
        if rec is not None and rec["pad"] is self.right and rec["zone"] == "bottom" and not rec["seen"]:
            self.jumpPulse = True

    def refresh(self):
        """Once per frame: turn the fingers into the four key states."""
        push = brake = jump = held = False
        for rec in self.fingers.values():
            rec["seen"] = True
            if rec["pad"] is self.left:
                if rec["zone"] == "top":
                    brake = True
                else:
                    push = True
            elif rec["pad"] is self.right:
                if rec["zone"] == "bottom":
                    jump = True
                if rec["latched"]:
                    held = True
        if self.jumpPulse:
            jump = True
            self.jumpPulse = False
        self.grindHeld = held
        s = self.state
        s["push"], s["brake"], s["jump"], s["grind"] = push, brake, jump, held

    def grindTick(self):
        """Once per 1/60 s game tick. True while the touch player counts as 'holding grind'."""
        for rec in self.fingers.values():          # thumb slid from GRIND to JUMP: release grind shortly after
            if rec["pad"] is self.right and rec["latched"] and rec["zone"] == "bottom":
                rec["slide"] -= 1
                if rec["slide"] <= 0:
                    rec["latched"] = False
                    self.grindHeld = any(f["latched"] for f in self.fingers.values())
                    if not self.grindHeld:
                        self.armTicks = 0
        if self.grindHeld:
            self.armTicks = GRIND_GRACE_TICKS
        elif self.armTicks > 0:
            self.armTicks -= 1
        # landed on something while grind was on -> stay engaged until we are off it again
        if player.grindBool and self.lastGrind:
            self.engaged = True
        elif not player.grindBool:
            self.engaged = False
        self.lastGrind = self.grindHeld or self.armTicks > 0 or self.engaged
        return self.lastGrind

    # ---------------- drawing ----------------
    def padStates(self):
        s = self.state
        grindOn = self.grindHeld or self.armTicks > 0 or self.engaged
        return (s["brake"], s["push"]), (grindOn, s["jump"])

    def drawOverlay(self):
        """Landscape without side bars: translucent pads on top of the game (only once a finger has touched)."""
        if not self.active or self.mode != "overlay":
            return
        (lt, lb), (rt, rb) = self.padStates()
        self.left.draw(screen, lt, lb)
        self.right.draw(screen, rt, rb)

    def drawPanel(self, surface, top=0):
        """Portrait: the black control box under the game. Landscape bars: the two black side bars."""
        if self.mode == "portrait":
            drawRoad(surface, top)
            surface.blit(self.panelHint, self.panelHintRect)
        elif self.mode == "bars":
            for r in self.barRects:
                surface.fill(BAR_COLOR, r)
            surface.fill((70, 72, 86), pg.rect.Rect(self.barRects[0].right - 2, 0, 2, height))
            surface.fill((70, 72, 86), pg.rect.Rect(self.barRects[1].x, 0, 2, height))
        else:
            return
        (lt, lb), (rt, rb) = self.padStates()
        self.left.draw(surface, lt, lb)
        self.right.draw(surface, rt, rb)

    def drawControlsHint(self):
        if self.active:
            screen.blit(self.hint, self.hintRect)

touch = TouchControls()

# Lets the existing code keep writing keys[pg.K_d], keys[pg.K_SPACE] ... : the touch buttons
# simply count as those keys being held.
class InputKeys():
    def __init__(self):
        self.real = pg.key.get_pressed()
        self.extra = {pg.K_d: False, pg.K_a: False, pg.K_SPACE: False}

    def update(self, real, touchControls):
        self.real = real
        self.extra[pg.K_d] = touchControls.state["push"]
        self.extra[pg.K_a] = touchControls.state["brake"]
        self.extra[pg.K_SPACE] = touchControls.state["jump"]

    def __getitem__(self, key):
        return self.real[key] or self.extra.get(key, False)

keys = InputKeys()
kbShift = False
tempInt = 0
menuButtons = [playButton, playAgainButton, controlsButton, menuButton, objectiveButton]

leaderboard = Leaderboard()

# Portrait: the road at the bottom of the game picture carries on down behind the pads (fading to dark),
# with lane dashes that scroll as the skater speeds up, so the whole screen looks like part of the game.
roadCache = {}
lanePos = 0.0
def drawRoad(surface, top):
    global lanePos
    h = displayH - top
    key = (top, displayH)
    g = roadCache.get(key)
    if g is None:
        c = gameSurface.get_at((width // 2, height - 1))
        g = pg.Surface((width, h)).convert()
        for yy in range(h):
            t = min(1.0, yy / 240.0)
            g.fill(tuple(int(c[i] + (PANEL_COLOR[i] - c[i]) * t) for i in range(3)), (0, yy, width, 1))
        roadCache[key] = g
    surface.blit(g, (0, top))
    lanePos = (lanePos + abs(player.dx) * PORTRAIT_ZOOM) % 160
    for k in range(-1, 6):
        surface.fill((205, 205, 215), (int(k * 160 - lanePos), top + 44, 70, 6))

# frame state for the zoomed portrait view
gameSurfaceBuf = None      # portrait only: offscreen 800x450 game picture
hudLayer = None            # portrait only: score + collectibles, drawn unzoomed on top
zoomSrc = zoomDest = None
frameZoom = False          # True when the frame that was just drawn is live gameplay (zoomed in portrait)

def fingerAsMouse(event):
    """Menu buttons listen for mouse clicks; turn finger taps into the same thing (in game pixels)."""
    if event.type == pg.FINGERDOWN:
        return pg.event.Event(pg.MOUSEBUTTONDOWN, pos=(int(event.x*displayW) - barOffset, int(event.y*displayH)), button=1)
    if event.type == pg.FINGERUP:
        return pg.event.Event(pg.MOUSEBUTTONUP, pos=(int(event.x*displayW) - barOffset, int(event.y*displayH)), button=1)
    return None

def gameEvent(event):
    """Real mouse clicks come in window pixels; with side bars the game starts barOffset pixels in."""
    if barOffset and event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
        return pg.event.Event(event.type, pos=(event.pos[0] - barOffset, event.pos[1]),
                              button=getattr(event, "button", 1), touch=getattr(event, "touch", False))
    return event

def goToMenu():
    """Back to the main menu with everything reset (the M key, and leaving the page)."""
    global gameActive
    grindLandSlide.stop()
    rollingSound.stop()
    controlsButton.mouseBool = False
    mainMenu.menuBool = True
    endScreen.endBool = False #og value uncomment
    endScreen.dispScoreBool = False
    leaderboard.cancel()
    gameActive = False #UNCOMMENT
    obstacle1.ObstacleRect.x = width
    player.reset(player_xPos,player_yPos)

# ---------------------------------------------------------------------------
# LEAVING THE GAME (page hidden, phone screen off, tab closed)
# ---------------------------------------------------------------------------
# The embed page on your website already unloads the whole game in these cases (that is the
# reliable part). This is the second line of defence from inside the game: a small JavaScript
# listener raises a flag, and when we notice it we silence everything and go back to the menu.
leaveSuspended = False

def installLeaveHooks():
    jsEval("""(function(){
      if (window.__skHooked) return; window.__skHooked = 1; window.__skHidden = 0;
      function audio(on){ try { var c = Module.SDL2 && Module.SDL2.audioContext; if (c) { on ? c.resume() : c.suspend(); } } catch(e){} }
      function gone(){ window.__skHidden = 1; audio(false); }
      var addL = window.addEventListener;
      addL.call(window, 'beforeunload', function(){          // page is being left: go quiet, come back if they stay
        audio(false);
        setTimeout(function(){ if (!document.hidden && !window.__skHidden) audio(true); }, 1500);
      });
      try { window.onbeforeunload = null; } catch(e){}
      window.addEventListener = function(t, f, c){ if (t === 'beforeunload') return; return addL.call(this, t, f, c); };
      document.addEventListener('visibilitychange', function(){ if (document.hidden) gone(); else audio(true); });
      window.addEventListener('pagehide', gone);
      window.addEventListener('message', function(e){ if (e.data === 'sk-leave') gone(); });
    })()""")

def suspendGame():
    try:
        pg.mixer.music.stop()
        pg.mixer.stop()
    except Exception:
        pass
    goToMenu()
    touch.fingers.clear()
    touch.armTicks = 0
    touch.engaged = False
    for b in menuButtons:
        b.mouseBool = False
        b.selectBool = False
        b.releasePending = False

def pollLeave():
    """A few times a second: did the page get hidden / closed? (browser only)"""
    global leaveSuspended
    if _platform is None:
        return
    if jsEval("window.__skHidden||0"):
        suspendGame()
        leaveSuspended = True
        jsEval("window.__skHidden=0")
    if leaveSuspended and not jsEval("document.hidden?1:0"):
        leaveSuspended = False
        startMusic()                     # back on the page: menu is showing, music returns

def handleEvents():
    global running, gameActive, kbShift
    for event in pg.event.get():

        if event.type == pg.QUIT:
            pg.quit() #opposite of pg init
            sys.exit(0) #stops while loop and ends cleanly

        gev = gameEvent(event)
        asMouse = fingerAsMouse(event)

        # the initials pop-up takes all input while it is open
        if leaderboard.entering:
            touch.handleEvent(event)
            leaderboard.handleEvent(event, gev, asMouse)
            continue

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.mixer.stop()
                pg.quit()
                sys.exit(0)
            if event.key == pg.K_m:
                #if the menu key is hit then reset all characters and obstacles
                goToMenu()

            if event.key in (pg.K_LSHIFT, pg.K_RSHIFT):
                kbShift = True

        elif event.type == pg.KEYUP:
            if event.key in (pg.K_LSHIFT, pg.K_RSHIFT):
                kbShift = False

        # touch screen (jump / push / brake / grind buttons)
        touch.handleEvent(event)

        #PASS EVENTS TO OTHER OBJECTS IN CLASSES:
        for btn in menuButtons:
            btn.playerInput(gev)
            if asMouse is not None:
                btn.playerInput(asMouse)

        if gameActive == True:
            pass

        else:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    resetALL()

def gameStep(dt):
    """Advance the game by exactly one 1/60 s tick (and draw it to `screen`)."""
    global gameActive, specialItemSpawnCounter, spawnSpecialItemBool, tempInt, screen, frameZoom

    # ENTER MAIN MENU
    if mainMenu.menuBool == True and endScreen.endBool == False:
        mainMenu.update()
    elif mainMenu.menuBool == False and endScreen.endBool == False:
        gameActive = True
    else:
        pass

    #Do the following only if the game is active
    if gameActive == True:

        #---------------------------------------

        #BLITTING CHARACTERS, BACKGROUND, AND OBJECTS ON THE SCREEN

        frameZoom = True
        # portrait: the score and collectibles go to their own layer so they are not zoomed
        hudOn = touch.portrait and screen is gameSurface
        if hudOn:
            hudLayer.fill((0, 0, 0, 0))
        # #background and text
        sky.update()
        bgBirds.update()
        world.update()
        bgPowerLines.update()
        obstacle1.update()

        sky.draw()
        bgBirds.draw()
        world.draw()
        nPC.update(dt)
        bgPowerLines.draw() #placed after npc to hide him behind the power lines
        if hudOn:
            screen = hudLayer
        specialItemDisp.update(dt)
        if hudOn:
            screen = gameSurface
        obstacle1.draw()
        cash.update()
        player.shiftPressed = kbShift or touch.grindTick()   # keyboard shift OR touch GRIND pad
        player.update(dt)
        if hudOn:
            screen = hudLayer
        displayScore()
        if hudOn:
            screen = gameSurface
        touch.drawOverlay()   # landscape only (portrait draws its pads under the game)



        #randomly spawn special items so it feels more random and unique
        specialItemSpawnInt = random.randint(0, len(spawnSpecialItemList)-1)
        if spawnSpecialItemBool == True:
            spawnSpecialItemList[specialItemSpawnInt].update(dt)
            tempInt = specialItemSpawnInt
            spawnSpecialItemBool = False
        else:
            specialItemSpawnCounter += 1*dt
            if spawnSpecialItemList[tempInt].rect.right > 0: #only update if it is on the screen
                spawnSpecialItemList[tempInt].update(dt)
            else:
                spawnSpecialItemList[tempInt].rect.right = -201 #this will trigger the class in the tracking to move it to the right
            if spawnSpecialItemList[tempInt].spawnItem == False: #only false if item count is zero meaning all collected
                spawnSpecialItemBool = True
            if spawnSpecialItemList[tempInt].rect.right <0: #spawnSpecialItemList[tempInt].spawnNewTrigger == True:
                if specialItemSpawnCounter >= 500*dt: #make higher for more sparse spawning

                    spawnSpecialItemList[specialItemSpawnInt].update(dt)
                    spawnSpecialItemBool = True
                    specialItemSpawnCounter = 0


        if finalSpecialItemCount() == totalSpecialPartsList(): #should be 15 items
            if completeDeck.itemCount != 0:
                completeDeck.update(dt)
            if completeDeck.rect.right < 0:
                completeDeck.rect.right = -201

        #LOSE CONDITION:
        if player.loseConditionBool == True:
            gameActive = False
            endScreen.endBool = True
            pass

    else: #if game is not active do this below
        frameZoom = False
        if endScreen.endBool == True:
            endScreen.update(dt)
        pass
    (hudLayer if (frameZoom and touch.portrait and screen is gameSurface) else screen).blit(versionSurf, (0,0))

def applyLayout(newW, newH, newBar):
    """Switch between: normal window | phone upright (taller) | phone sideways with side bars (wider)."""
    global display, gameSurface, screen, displayW, displayH, barOffset, hudLayer, zoomSrc, zoomDest
    displayW, displayH, barOffset = newW, newH, newBar
    display = pg.display.set_mode((newW, newH))
    roadCache.clear()
    if newH > height:
        # upright: the game is drawn on an offscreen 800x450 picture; the part we show is scaled up into
        # the top of the window (composePortrait), the score/collectibles layer goes on top unzoomed.
        gameSurface = pg.Surface((width, height)).convert()
        hudLayer = pg.Surface((width, HUD_H), pg.SRCALPHA).convert_alpha()
        zoomSrc = gameSurface.subsurface(pg.rect.Rect(0, 0, ZOOM_W, height))
        zoomDest = display.subsurface(pg.rect.Rect(0, 0, width, ZOOM_H))
    elif newBar:
        gameSurface = display.subsurface(pg.rect.Rect(newBar, 0, width, height))
    else:
        gameSurface = display
    screen = gameSurface
    touch.setLayout(newW, newH, newBar)

def composePortrait():
    """Portrait: zoomed gameplay (or the plain 800x450 picture for menus) + black control box."""
    if frameZoom:
        pg.transform.scale(zoomSrc, (width, ZOOM_H), zoomDest)
        display.blit(hudLayer, (0, 0))
        top = ZOOM_H
    else:
        display.blit(gameSurface, (0, 0))
        top = height
    touch.drawPanel(display, top)


async def main():
    global screen, keys, running
    dummyScreen = pg.Surface((1, 1))   # catch-up ticks draw here (nobody sees them)
    accumulator = 0.0
    frameNum = 0
    touchDevice = isTouchDevice()
    installLeaveHooks()

    while running:
        # real time since the last frame (clock.tick also caps us at 60 fps)
        accumulator += min(clock.tick(60) / 1000, MAX_FRAME_TIME)

        frameNum += 1
        # a few times a second: is the page tall (phone upright), wide (sideways) ...?
        if touchDevice and frameNum % 15 == 1:
            nw, nh, nb = wantedLayout(touchDevice)
            changed = (nw != displayW) or (nb != barOffset)
            if nh != displayH and (nh == height or displayH == height or abs(nh - displayH) > 24):
                changed = True
            if changed:
                applyLayout(nw, nh, nb)
        if frameNum % 10 == 3:
            pollLeave()
        if frameNum % 30 == 7:
            leaderboard.pollRemote()

        handleEvents()
        touch.refresh()
        keys.update(pg.key.get_pressed(), touch)
        player.jumpMobile = touch.state["jump"]

        # How many 1/60 s game ticks are owed? (small tolerance stops jitter on 60 Hz screens)
        steps = int((accumulator + FIXED_DT*0.1) / FIXED_DT)
        if steps > MAX_STEPS_PER_FRAME:
            steps = MAX_STEPS_PER_FRAME
            accumulator = 0.0           # too far behind: stop trying to catch up
        else:
            accumulator -= steps * FIXED_DT

        # Only the last tick of a frame is drawn for real. If the computer is slow and
        # several ticks are owed, the earlier ones just move things (no drawing), so the
        # game keeps the right speed instead of running in slow motion.
        for i in range(steps):
            screen = gameSurface if i == steps - 1 else dummyScreen
            gameStep(FIXED_DT)
        screen = gameSurface

        if steps > 0:
            for btn in menuButtons:
                btn.endFrame()
            if touch.mode == "portrait":
                composePortrait()            # zoomed game + black control box with the pads
            elif touch.mode == "bars":
                touch.drawPanel(display)     # the two black side bars with the pads
            #refreshes the screen (at most 60 times a second)
            pg.display.flip()

        await asyncio.sleep(0)   # required by pygbag: lets the browser breathe every frame

#debugging delete later:
gameActive = False
mainMenu.menuBool = True

asyncio.run(main())
