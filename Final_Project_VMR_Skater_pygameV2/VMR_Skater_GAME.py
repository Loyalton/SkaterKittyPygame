import pygame as pg
import sys
import random

pg.init()
pg.mixer.init()

# display screen and basic set up
width = 1280
height = 720
resolution = (width, height)
screen = pg.display.set_mode(resolution)
clock = pg.time.Clock()

#fonts for displaying text
textFont1 = pg.font.Font(None, 50) # None can be changes to specify a font type
textFont2 = pg.font.Font(None, 25) # 25 is a smaller font size than the above

# listFonts = pg.font.get_fonts()
# print(listFonts)
"we could make this a list of fonts and use an index to select between them"

#setting the display window caption
pg.display.set_caption("Skater Kitty")


#loading all the images
disp_icon = pg.image.load("graphics/HeadofKittyBoardBluntLoyalton.png").convert_alpha()

enemy1 = pg.image.load("graphics/BnWKittyBoardBluntLoyalton.png").convert_alpha()

#place images to respective locations
pg.display.set_icon(disp_icon) #load it to the display window

#starting positions
player_xPos = 250
player_yPos = 675
player_xPos1 = 1280
player_yPos1 = 675

#setting up booleans
running = True
gameActive = False

#Import Audio Files:
rolling = pg.mixer.Sound("audio/rolling.wav")
bgMusic = pg.mixer.Sound("audio/RomanoBeatbyLoyalton.mp3")
ambientSound = pg.mixer.Sound("audio/ambientOutdoorSounds.mp3")
cashSound = pg.mixer.Sound("audio/cash.mp3")
#skateboard sounds
ollieUpSound = pg.mixer.Sound("audio/ollieUp.mp3")
ollieDownSound = pg.mixer.Sound("audio/ollieDown.mp3")
rollingSound = pg.mixer.Sound("audio/rollingshort.mp3")
specialCollectSound = pg.mixer.Sound("audio/specialItemSound.mp3")
specialCollectSound.set_volume(0.25)

#bail sounds
livBailVoice = pg.mixer.Sound("audio/livCrashVoice.mp3")
dorBailVoice = pg.mixer.Sound("audio/dorCrashVoice.mp3")
boardHitObj = pg.mixer.Sound("audio/boardHitObj.mp3")
bailSound = pg.mixer.Sound("audio/bailSoundBoard.mp3")
bailSoundTopple = pg.mixer.Sound("audio/bailSoundBoardTopple.mp3")

grindLand = pg.mixer.Sound("audio/grindLandMetal.mp3")
grindLandSlide = pg.mixer.Sound("audio/grindLandSlideRail.mp3")
grindSlide = pg.mixer.Sound("audio/grindSlideMetal.mp3")
grindPack = [grindLand, grindLandSlide, grindSlide]
#play sound
bgMusic.play(-1) #-1 means to loop indefinitely
ambientSound.play(-1)
ambientSound.set_volume(0.05)




#CLASSES: for making the game more organized

class Sounds():
    def __init__(self) -> None:
        pass

class World():
    
    def __init__(self, imgSelect = 0, bgspeed = 0, fontIndex = 0):
        self.counterFont = 0
        imgSelect = imgSelect
        bgspeed = bgspeed

        self.reset(imgSelect, bgspeed, fontIndex)

        # self.reset(None)
    def reset(self, imgSelect, bgspeed, fontIndex=None):
        #load images
        #below we will have all the images relates to the world building and levels
        #we will have a list to be able to choose an index to change things
        #--------------------------------------------------------------------

        self.bg_List = [
            pg.image.load("graphics/sky.png").convert_alpha(),
            pg.image.load("graphics/bgBuildings.png").convert_alpha(),
            pg.image.load("graphics/bgPowerLines.png").convert_alpha(),
            pg.image.load("graphics/bgBirds.png").convert_alpha()
            ]
        
        #background list
        self.bg_Index = imgSelect
        self.bgSelect = self.bg_List[self.bg_Index]

        # SCALE DOWN img:
        "as long as the backgrounds are the same size this is ok if not then need to do logic similar to player animation"
        # self.ratio = 1280*3 = 3840
        scaleNum = 1/2 #change this to scale original image
        self.imgSize = self.bgSelect.get_size()
        self.imgScaled = (self.imgSize[0]*scaleNum, self.imgSize[1]*scaleNum)

        img = pg.transform.smoothscale(self.bgSelect, self.imgScaled)

        #final after all mods
        self.background = img #self.bg_List[self.bg_Index]

        #--------------------------------------------------------------------

        #game name text

        # self.textFont1 = pg.font.Font(self.fontList[self.fontIndex], 50) #add text files 
        self.gameNameSurf = textFont1.render("STREET SKATER!", True, 'Black')
        self.GameNameRect = self.gameNameSurf.get_rect(center=(width/2, 100))
        # self.GameNameRect.center = (width/2, 100)

        #starting position of background
        self.bgStartPosx = 0 #this will be used to scroll
        self.bgStartPosy = 0 #this probably won't need to change

        self.bgRect = pg.Surface.get_rect(self.background)
        self.bgRect.topleft = (self.bgStartPosx, self.bgStartPosy)

        #for movement
        self.bgMove = False
        self.kMoveBool = False

        # if self.kMoveBool == True:
        #     self.bgSpeed = bgspeed
        #     print(bgspeed)

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
        # self.bgSpeed = 3 # this is old not needed here anymore used for constant speed

    def change_background(self, new_index):
        if 0 <= new_index < len(self.bg_List):
            self.bg_index = new_index
            self.background = self.bg_List[self.bg_index]
        else:

            print(f"Error: Invalid background index {new_index}")

    def update(self):

        if self.bgMove == True and self.kMoveBool == False:
            self.bgStartPosx -= abs(player.dx)/6#+self.bgSpeed
            if player.dx == 0:
                self.bgMove = False
        elif self.kMoveBool == True:
            self.bgStartPosx -= self.bgSpeed
        # if self.bgRect.right <= 0:
        #         self.bgStartPosx = 0 

        #if the background has fully scrolled off the screen, reset position
        if self.bgStartPosx <= -self.background.get_width():
            self.bgStartPosx = 0
            # print("left")

        # if self.counterFont == 20:
        #     self.fontIndex += 1
        #     self.reset(self.fontIndex)

    def draw(self, screen):
        screen.blit(self.background, (self.bgStartPosx, self.bgStartPosy))
        screen.blit(self.background, (self.bgStartPosx+self.background.get_width(), self.bgStartPosy)) #twice for seamless repetition

        # pg.draw.rect(screen, (255, 0, 0), self.bgRect, 2)
        if self.kMoveBool == False:
            # screen.blit(self.gameNameSurf, (self.GameNameRect))
            "move game name to Main Menu??? for now"
            pass 

class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def reset(self, x, y):

        self.img = self.ollieImages = [
            pg.image.load("graphics/player1.png").convert_alpha(),
            pg.image.load("graphics/player2.png").convert_alpha(),
            pg.image.load("graphics/player3.png").convert_alpha(),
            pg.image.load("graphics/player4.png").convert_alpha()
        ]
        self.current_image_index = 0

        self.imgSelect = self.ollieImages[self.current_image_index]

        

        self.scaleNum = 1/13 #change this to scale original image
        self.imgSize = self.imgSelect.get_size()  #original image size
        new_width = int(self.imgSize[0] * self.scaleNum)
        new_height = int(self.imgSize[1] * self.scaleNum)
        self.imgScale = (new_width, new_height)
        # print("New size:", self.imgScale)
       
        self.player = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        # self.Obstacle = pg.transform.smoothscale(self.img[2], self.imgScale)
        self.playerRect = self.player.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.playerRect.midbottom = (x,y)
        # self.playerRect.x = x
        # self.playerRect.y = y
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
        self.grindKeyBool = False
        self.loseConditionBool = False
        self.platformBool = False
        

        #counter for speed and accelleration control
        self.dx = 0
        self.dy = 0
        self.acceleration = 0.35/2  
        self.deceleration = 0.05
        self.max_speed = 12 #12 feels like a good speed  
        self.movingRight = False
        self.movingLeft = False
        self.RailOllie = False

        #bools for Sound
        self.playRolling = False

        #temp rect
        self.tempPosAdj = 20
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
                  

    def playerInput(self):
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

        if keys[pg.K_SPACE]:
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
                self.gravity = -25
                ollieUpSound.play()
                ollieUpSound.set_volume(0.5)
                self.inAirBool = True
            self.spaceBarHeld = False
        #--------------------------------------------------------

        if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT]:
            self.grindKeyBool = True
        else:
            self.grindKeyBool = False

        #quit game
        if keys[pg.K_ESCAPE]:
            exit(0)

    def collision(self, rect, currPosPass):
        
        if obstacle1.ObstacleRect.colliderect(self.tempRectx):
            # rollingSound.stop()
            
            if obstacle1.ObstacleRect.left < self.playerRect.right-25: #adjust num if needed -25 is good
                pass

            elif obstacle1.ObstacleRect.left <= self.playerRect.right:
                "BAIL IN X POS"
                # print("BAIL!!!!!!!!!!!!!!!!!!!!!!!")
                "there may be a condition where this falsely triggers but I think it's ok for now"
                rollingSound.stop()
                self.dx = 0
                self.loseConditionBool = True
                print("loseloselose in x dir", self.loseConditionBool)
                "issue: triggered but not ending game" #Resolved was due to elif below was only if
                "ADD BAIL SOUND HERE"
                
                if self.bailBool == False:
                    # rollingSound.set_volume(0.15)
                    # grindLand.play()
                    boardHitObj.play()
                    livBailVoice.play()  # Play in loop mode
                    # dorBailVoice.play()
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
                
            if obstacle1.ObstacleRect.top+20 > self.playerRect.bottom > obstacle1.ObstacleRect.top and self.grindKeyBool == True: 
                
                rollingSound.stop()
                "grind enable Vertical range "
                if keys[pg.K_SPACE]:
                    # self.inAirBool = False
                    ollieUpSound.play()
                    self.gravity = -25
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
                if self.playerRect.bottom > obstacle1.ObstacleRect.top+20:
                    "TO DO: 11/10/2024"
                    " find a way to register the range that is out of bounds when exiting the grinding if statement above" #resolved
                    print("Below grind range")

                    if self.playerRect.left+self.surf.get_width()*0.25 < obstacle1.ObstacleRect.right:
                        print("NOT safe range for exiting grind")
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
                        print("Out of BAIL range")
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
            print("BAIL!!!!!")
            grindLandSlide.stop()
            gameActive = False
            pass
    
    def animation(self):
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
            self.ollieCounter += 1
            
            if self.ollieCounter >= self.ollieAnimationSpeed:
                self.ollieCounter = 0
                if self.current_image_index < len(self.ollieImages) - 1:
                    self.counterFrame += 1
                    self.current_image_index = 2
                    if self.counterFrame == 3: #change value to adjust how long slide up image is held
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

    def applyGravity(self):
        # print(self.gravity)
        self.gravity += 1
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
        self.imgSize = self.imgSelect.get_size()
        new_width = int(self.imgSize[0] * self.scaleNum)
        new_height = int(self.imgSize[1] * self.scaleNum)
        self.imgScale = (new_width, new_height)

        # scale and also update the rect dimensions based on new loaded image
        self.surf = self.player = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.playerRect = self.player.get_rect()

        self.playerRect.midbottom = self.curPosPass#(player_xPos, self.currentPos[1])
        # self.collision(self.playerRect, self.curPosPass)
        self.draw(self.surf, self.playerRect)

        #temp rect
        self.tempRectx = pg.rect.Rect(self.playerRect[0]+self.tempPosAdj, self.playerRect[1], self.playerRect.w, self.playerRect.h)
        self.tempRectx.bottom = self.playerRect.bottom-self.tempPosAdj

        self.tempRecty = pg.rect.Rect(self.playerRect[0], self.playerRect[1]+self.tempPosAdj, self.playerRect.w, self.playerRect.h)
        self.tempRecty.right = self.playerRect.right-self.tempPosAdj
        self.tempRecty.bottom = self.playerRect.bottom + self.tempPosAdj
        
        #draw player on screen
        # screen.blit(self.surf, self.playerRect)
        # pg.draw.rect(screen, (255, 0, 0), self.playerRect, 2) #to visualize the rect around image      

    def change_image(self, new_index, curPos):
        # change image and draw new rect with correct dimensions no squashing or stretch
        if 0 <= new_index < len(self.img):
            self.update_image(new_index, curPos)
 
    "for some reason could not pass object to draw() would not blit correctly, now done in update_image()" #resolved
    def draw(self, surf, curPOSRect):
        
        "use three lines below to visualize for collision logic" #diasble for final game
        # pg.draw.rect(surface=screen, color="blue", rect=self.tempRectx, width=2)
        # pg.draw.rect(surface=screen, color="green", rect=self.tempRecty, width=2)
        # pg.draw.rect(screen, (255, 0, 0), self.playerRect, 2) #to visualize the rect around image

        screen.blit(surf, curPOSRect)
        


    def update(self):
        #draw player onto screen
        self.curPosPass = self.playerRect.midbottom

        # pg.draw.rect(screen, (255, 0, 0), boardRect, 2)
        # self.playerInput()
        self.playerMotion()
        self.playerInput()
        self.collision(self.playerRect, self.curPosPass)
        self.animation()
        self.applyGravity()
        
        # screen.blit(self.player, self.curPosPass)
        
        
        "if we want the character to move on the screen add these"
        # #BOUNDARIES: not in use if player doesn't move horizontally
        # if self.playerRect.right >= width:
        #     self.playerRect.right = width
        # if self.playerRect.left <= 0:
        #     self.playerRect.left = 0
        # # boardRect.midtop = (player.playerRect.midbottom[0]-10, player.playerRect.midbottom[1]-15)

class Skateboard: #not in use at the moment
    def __init__(self):
        self.board = pg.image.load("graphics/skateboard.png")
        self.board = pg.transform.rotozoom(self.board, 0, 0.1)
        self.boardRect = self.board.get_rect()
    
    def update(self):
        #skateboard position based on the player's position though may change with drawing
        self.boardRect.midtop = (NPC1.NPC1Rect.midbottom[0], NPC1.NPC1Rect.midbottom[1]-5)
        self.draw()
    
    def draw(self):
        screen.blit(self.board, self.boardRect)
        # pg.draw.rect(screen, (255, 0, 0), self.boardRect, 2)

class NPC():
    def __init__(self, x, y):
       
        NPCSurf1 = pg.image.load("graphics/NPC1.png").convert_alpha()
        NPCSurf2 = pg.image.load("graphics/NPC2.png").convert_alpha()
        self.NPC1List = [NPCSurf1, NPCSurf2]
        self.NPC1_index = 0
        self.NPC1_Select = self.NPC1List[self.NPC1_index]

        scaleNum = 1/25 #change this to scale original image
        playerImageSize = self.NPC1_Select.get_size() #(240, 300)
        self.playerScale = (playerImageSize[0]*scaleNum, playerImageSize[1]*scaleNum)
        self.playerSize = (self.playerScale) #for rotozoom if you want 2x bigger just a 2, if use scale need tuple (100,100)

        self.NPC1 = pg.transform.smoothscale(self.NPC1_Select, self.playerSize) #this is my new surface
        self.NPC1Rect = self.NPC1.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        
        self.startposx = 0
        self.NPC1Rect.x = x+self.startposx
        self.NPC1Rect.y = y
        self.NPC1Rect.midbottom = (self.NPC1Rect.x, height*6/7 -10)

        # Time tracking variables
        #Switch between images
        self.last_switch_time = pg.time.get_ticks()  # To track when the last image switch happened
        self.switch_duration = 1000 # x second (for switching)
        self.normal_duration = 4000  # x seconds (between switches
        self.switched = False

        # Create bounce effect
        self.last_switch_time2 = pg.time.get_ticks()
        self.switch_duration2 = 100  # x second (for switching)
        self.normal_duration2 = 100 # x seconds (between switches
        self.switched2 = False

    def animation(self):
        #random integer for placement use
        self.randInt = random.randint(0,3)
        self.rantIntx = random.randint(player_xPos, width)

        #get the current time in milliseconds
        current_time = pg.time.get_ticks()

        #if duration x seconds have passed, switch to the second image
        if not self.switched and current_time - self.last_switch_time > self.normal_duration:
            self.NPC1_Select = self.NPC1List[1]  # Switch to the second image
            self.NPC1 = pg.transform.smoothscale(self.NPC1_Select, self.playerSize)
            self.last_switch_time = current_time  # Reset the timer
            self.switched = True  

        #if duration x seconds has passed in the switched state, return to the first image
        elif self.switched and current_time - self.last_switch_time > self.switch_duration:
            self.NPC1_Select = self.NPC1List[0]  # Switch back to the first image
            self.NPC1 = pg.transform.smoothscale(self.NPC1_Select, self.playerSize)
            self.switched = False

        # #create a bounce effect
        "the bounce effect wasn't looking right if he's moving. add if he's static"
        # if not self.switched2 and current_time - self.last_switch_time2 > self.normal_duration2:
        #     self.NPC1Rect.y = self.NPC1Rect.y+1
        #     self.last_switch_time2 = current_time  # Reset the timer
        #     self.switched2 = True  # Set the switch flag
        # elif self.switched2 and current_time - self.last_switch_time2 > self.switch_duration2:
        #     self.NPC1Rect.y = self.NPC1Rect.y-1
        #     self.switched2 = False
        #     self.last_switch_time2 = current_time
        

        # randInt

        #movement horizontally for npc
        self.NPC1Rect.right -= abs(player.dx)/6 + self.randInt
        if self.NPC1Rect.x < -200:
            self.NPC1Rect.left  = width*(self.randInt+2) + self.rantIntx #resetting npc to random pos to right of screen

        "could add sound that increases depending on the x position of the rat to play rolling sound"


    def update(self):
        self.animation()      
        
        #draw player onto screen
        screen.blit(self.NPC1, self.NPC1Rect)
        # pg.draw.rect(screen, color="red", rect=self.NPC1Rect, width=2)
        
class EndScreen():

    def __init__(self):
        #creating text surfaces to blit later
        # gameNameSurf = textFont1.render("My Game!", True, 'Black') # second arg is for Anti Aliasing (smoothing edges) set to True or False
        "maybe not needed use button class instead"
        self.scalenum = 0.30
        self.img = pg.image.load("graphics/statsMenu.png").convert_alpha()
        self.imgSize = self.img.get_size()
        self.imgScaled = (self.imgSize[0]*self.scalenum, self.imgSize[1]*self.scalenum)
        self.statsMenuSurf = pg.transform.smoothscale(self.img, self.imgScaled)
        self.statsMenuRect = self.statsMenuSurf.get_rect()
        self.statsMenuRect.center = (250, height-300)


        self.countEnd = 0
        self.maxEndCount = 75
        self.countBool = False
        self.endBool = False
        self.endGameTextSurf = textFont1.render("End Game!", True, (0,0,0))
        self.endGameTextSurf = textFont1.render("End Game!", True, (255,0,0))

        self.blinkTextRect = self.endGameTextSurf.get_rect()
        self.blinkTextRect.center = (width/2, height/2 -100)
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
            self.endGameTextSurf = textFont1.render(self.blink_Text, True, self.blinkColor1)
        elif 0 < self.countEnd < self.maxEndCount and self.countBool == True:
            self.endGameTextSurf = textFont1.render(self.blink_Text, True, self.blinkColor2)
        elif self.countEnd == 0:
            self.countBool = False
            pass
        blinkingSurf = self.blink_Text
        return blinkingSurf
    
    def saveLog(self):
        #later change this section to only save once the game has ended then update the endScreen()

        if self.saveBool == False:
            #save special skate parts
            for item in range (0, len(spawnSpecialItemList) -1):
                self.lines = str(spawnSpecialItemList[item].finalItemcount)

                with open(f"saveParts{spawnSpecialItemList[item].imgIndex}.txt", mode="w", encoding="utf-8") as f:
                    self.lines = f.writelines(self.lines)
            self.saveBool = True

            #save cash
            self.lines = str(cash.cashcount)
            with open("saveCash.txt", mode="w", encoding="utf-8") as f:
                self.lines = f.writelines(self.lines)

            #save final time score
            lines = displayScore()
            with open("saveScore.txt", mode="w", encoding="utf-8") as f: #mode = "w" is for writing but clears wahatever data was there before
                lines = f.write(lines) #to read a single line
                # lines = f.writelines() #to read multiple lines

            with open("saveScore.txt", mode="r", encoding="utf-8") as f: #mode = "r" is for reading saved files you can also open something in a folder with "name_of_folder\save.txt"
                # lines = f.read(8) #to read a single line if you give it a number in the arguement it gives you a number of characters
                lines = f.readlines() #to read multiple lines if you give it a number in the arguement up to that number in characters you get the first name up to n name
                finalscore = lines[0].strip() 
                # print(lines)
            # finalScoreText = textFont1.render(f'Final Time: {finalscore}s', True, ("blue"))
            self.finalScoreText = textFont1.render(f'{finalscore}', True, ("blue"))
            self.finalScoreRect = self.finalScoreText.get_rect(center = (350, height-300))
            # screen.blit(finalScoreText, finalScoreRect)




    def update(self):
        self.saveLog()
        #update pos because main menu moves it out of the way
        playButton.buttonRect.center = (width/2, height/2)

        self.blinkText("END GAME!")    
        sky.update()
        bgBirds.update()
        sky.draw(screen)
        bgBirds.draw(screen)
        
        world.draw(screen)
        bgPowerLines.draw(screen)

        completeDeckDisp.rect.center = (width*4/5, height*3/5)
        boardSideLDisp.rect.center = (width*4/5, height*3/5)
        boardGripTapeDisp.rect.center = (width*4/5, height*3/5)
        boardSideRDisp.rect.center = (width*4/5, height*3/5)


        #this is to rotate the complete deck at the end screen but it doesn't do it smoothly but it is fine
        self.animationCounter += 1            
        if self.animationCounter > self.animationLimitNum*5:
            completeDeckDisp.update()
            self.animationCounter = self.animationLimitNum #this fixed it to be smoother
        elif self.animationCounter > self.animationLimitNum*4:
            completeDeckDisp.update()
        elif self.animationCounter > self.animationLimitNum*3:
            boardSideRDisp.update()
        elif self.animationCounter > self.animationLimitNum*2:
            boardGripTapeDisp.update()
        elif self.animationCounter > self.animationLimitNum*1:
            boardSideLDisp.update()
        elif self.animationCounter > 0:
            completeDeckDisp.update()
        else:
            pass

        if playAgainButton.mouseBool == True or keys[pg.K_RETURN] == True or keys[pg.K_KP_ENTER] == True:
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
            resetALL()

        elif menuButton.mouseBool == True:
            playButton.buttonRect.bottom = width/2 
            playAgainButton.buttonRect.bottom = 0
            controlsButton.buttonRect.bottom = height-250
            menuButton.buttonRect.bottom = 0
            controlsButton.selectBool = False
            controlsButton.mouseBool = False
            objectiveButton.selectBool = False
            objectiveButton.mouseBool = False
            self.endBool = False
            mainMenu.menuBool = True
            menuButton.mouseBool = False
            menuButton.selectBool = False
            
            # resetALL()
            # print("here menu")

        elif menuButton.mouseBool == False:
            # print("we are in else")
            #reset positions of buttons
            controlsButton.buttonRect.bottom = 0
            objectiveButton.buttonRect.bottom = 0


            playAgainButton.buttonRect.center = (width/2, height/2)
            menuButton.buttonRect.center = (width/2, height/2 +200)
            self.statsMenuRect.center = (250, height-300)
            menuButton.update()

            screen.blit(mainMenu.gameNameSurf, mainMenu.mainMenuRect)
            screen.blit(self.statsMenuSurf, self.statsMenuRect)
            playAgainButton.update()

            finalSpecialCount = finalSpecialItemCount() #to get the final count of special parts
            # print(finalSpecialCount)
            self.specialItemCount = textFont1.render(f'{finalSpecialCount}/15', True, ("black"))
            self.finalCashRect = self.specialItemCount.get_rect(center = (350, height-215))
            screen.blit(self.specialItemCount, self.finalCashRect)

            
            # screen.fill(color=(255,255,255))
            screen.blit(self.endGameTextSurf, self.blinkTextRect)#(540,300))
            # screen.blit(self.playAgainTextSurf, self.playAgainTextRect)# (450,400))      

            # displayScore()
            screen.blit(self.finalScoreText, self.finalScoreRect)
            cash.finalScore()
                    
class MainMenu():

    def __init__(self):
        #creating text surfaces to blit later
        # gameNameSurf = textFont1.render("My Game!", True, 'Black') # second arg is for Anti Aliasing (smoothing edges) set to True or False
        # self.mainMenuSurf = textFont1.render("MAIN MENU", True, 'white')
        self.playTextSurf = textFont1.render("Press Enter/Return to play!", True, 'white')

        #game Name
        self.img = pg.image.load("graphics/gameName5.png").convert_alpha()
        self.gameNameSurf = pg.transform.rotozoom(self.img, 0, 0.8)

        # controls menu
        self.scalenum2 = 0.4
        self.img2 = pg.image.load("graphics/controlsMenu.png").convert_alpha()
        self.imgSize = self.img2.get_size()
        self.imgScaled = (self.imgSize[0]*self.scalenum2, self.imgSize[1]*self.scalenum2)
        self.controlsMenuSurf = pg.transform.smoothscale(self.img2, self.imgScaled)
        # self.controlsMenuSurf = pg.transform.rotozoom(self.img2, 0, 0.4)

        # objective menu
        self.scalenum3 = 0.4
        self.img3 = pg.image.load("graphics/objectiveMenu.png").convert_alpha()
        self.imgSize = self.img3.get_size()
        self.imgScaled = (self.imgSize[0]*self.scalenum3, self.imgSize[1]*self.scalenum3)
        self.objectiveMenuSurf = pg.transform.smoothscale(self.img3, self.imgScaled) #this is better visually
        # self.objectiveMenuSurf = pg.transform.rotozoom(self.img3, 0, 0.4)




        # creating text rects
        self.mainMenuRect = pg.Surface.get_rect(self.gameNameSurf)
        self.mainMenuRect.center = (width/2, 150)

        self.controlsRect = pg.Surface.get_rect(self.controlsMenuSurf)
        self.controlsRect.center = (width/2, height/2 +100)

        self.objectiveRect = pg.Surface.get_rect(self.objectiveMenuSurf)
        self.objectiveRect.center = (width/2, height/2 +100)



        self.playTextRect = pg.Surface.get_rect(self.playTextSurf)
        self.playTextRect.center = (width/2, height*3/4)
        self.menuBool = True
        self.gameActive = False

    def update(self):
        # screen.fill(color=(255,255,255))
        if self.menuBool == True:
            sky.update()
            bgBirds.update()
            sky.draw(screen)
            bgBirds.draw(screen)
            world.draw(screen)
            bgPowerLines.draw(screen)
            screen.blit(self.gameNameSurf, self.mainMenuRect)
            # screen.blit(self.controlsMenuSurf, self.controlsRect)
            # screen.blit(self.playTextSurf, self.playTextRect)# (450,400))


            
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
                controlsButton.buttonRect.bottom = height-250
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
                menuButton.buttonRect.center = (250, height-200)

                menuButton.update()
                screen.blit(self.controlsMenuSurf, self.controlsRect)
                
                # self.menuBool = False
                # self.gameActive = True
                # playButton.mouseBool = False
                pass

            elif objectiveButton.selectBool == True:
                #move buttons out of the screen
                playButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0 
                controlsButton.buttonRect.bottom = 0
                menuButton.buttonRect.center = (250, height-200)

                menuButton.update()
                screen.blit(self.objectiveMenuSurf, self.objectiveRect)

            elif controlsButton.mouseBool == False and objectiveButton.mouseBool == False:
                #reset positions of buttons
                playButton.buttonRect.center = (width/2, height/2)
                controlsButton.buttonRect.center = (250, height-200)
                objectiveButton.buttonRect.center = (width-250, height-200)
                menuButton.buttonRect.bottom = 0


                # playButton.reset()
                playButton.update()
                controlsButton.update()
                objectiveButton.update()
            # endScreen.endBool = True
        # else:
        #     self.gameActive = False
            # playButton.buttonRect.clear #clear any enemies and obstacles reset
            

        # world.change_background(1)

class Button():
    def __init__(self, x, y, imgSelect, sizeButton):
        self.x = x
        self.y = y
        self.imgSelect = imgSelect
        self.sizeButton = sizeButton
        self.reset()

    def reset(self):
        self.img = [
            pg.image.load("graphics/playBlueButton3.png"),
            pg.image.load("graphics/controlsButton.png"),
            pg.image.load("graphics/menuButtonBlue.png").convert_alpha(),
            pg.image.load("graphics/menuButton.png").convert_alpha(),
            pg.image.load("graphics/objectiveButton.png").convert_alpha(),
            pg.image.load("graphics/playAgainButton.png").convert_alpha(),
            pg.image.load("graphics/youWinButton.png").convert_alpha(),
            pg.image.load("graphics/youWinButtonY.png").convert_alpha(),
            pg.image.load("graphics/youWinButtonB.png").convert_alpha()

        ]

        self.imgIndex = self.imgSelect
        self.imgSelect = self.img[self.imgIndex]

        scaleNum = self.sizeButton #change this to scale original image
        self.imgSize = self.imgSelect.get_size() #(240, 300)
        self.imgScale = (self.imgSize[0]*scaleNum, self.imgSize[1]*scaleNum)
       
        self.button = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.buttonRect = self.button.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.buttonRect.center = (self.x, self.y)
        # self.buttonRect.x = x
        # self.buttonRect.y = y

        self.mouseBool = False
        self.selectBool = False

    def playerInput(self, event): #takes event queue input to use here
        #Checking mouse clicks and positions within the event Section
        if event.type == pg.MOUSEBUTTONUP: #captures only when it is released once
            # print("mouse up")
            if event.button == 1 and self.buttonRect.collidepoint(event.pos): #checks if mouse collides with rect
                # print("collide")
                self.mouseBool = True
                if self.mouseBool == True:
                    self.selectBool = True
        else:
            self.mouseBool = False #moved logic to the main menu
            pass


        # if event.type == pg.MOUSEBUTTONDOWN: #captures only when it is pressed down once
        #     if event.button == 1:
        #         print("mouse down left")
        #     if event.button ==2:
        #         print("mouse wheel click")
        #     if event.button == 3:
        #         print("mouse right")
        # if event.type == pg.MOUSEMOTION: #gets the mouse position when it is moved on screen
        #     loc=pg.mouse.get_pos()
        #     # print(loc)
        #     # print("mouse moved")
        


        # #This section below prints when the mouse is over the character to get position
        # self.mousePos = pg.mouse.get_pos()
        # # print(mousePos)
        # if self.buttonRect.collidepoint((self.mousePos)): 
        #     print(self.mousePos)
        # pass

    def draw(self):
        screen.blit(self.button, self.buttonRect)
        pass

    def update(self):
        # self.playerInput()
        self.draw()
        
class Obstacles():
    def __init__(self, x, y):
        self.x=x
        self.y=y
        self.reset(self.x,self.y)

    def reset(self, x,y):
        self.img = [
            #platforms:
            # pg.image.load("graphics/blockandstairBlock.png"), # = 0 for list to check platform could use mapping

            # regular Obstacles
            pg.image.load("graphics/rail.png"),
            pg.image.load("graphics/railTall.png"),
            pg.image.load("graphics/railLong.png"),
            pg.image.load("graphics/railLong2x.png"),
            pg.image.load("graphics/cementBlock.png"),
            
            pg.image.load("graphics/cone.png"),
            pg.image.load("graphics/mailbox.png"),
            pg.image.load("graphics/meter.png"),
            pg.image.load("graphics/bench.png"),
            pg.image.load("graphics/barrier.png"),
            pg.image.load("graphics/bigCone.png"),
            pg.image.load("graphics/hydrant.png"),
            pg.image.load("graphics/trashCan.png")

        ]
        # print(len(self.img)-1)
        self.imgIndex = random.randint(0,len(self.img)-1)
        self.imgSelect = self.img[self.imgIndex]

        self.scaleNum = 1/6 #change this to scale original image
        # self.imgSize = self.imgSelect.get_size() #(240, 300)
        # self.imgScale = (self.imgSize[0]*scaleNum, self.imgSize[1]*scaleNum)

        self.imgSize = self.imgSelect.get_size()  # Original image size
        new_width = int(self.imgSize[0] * self.scaleNum)
        new_height = int(self.imgSize[1] * self.scaleNum)
        self.imgScale = (new_width, new_height)
       
        self.Obstacle = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        # self.Obstacle = pg.transform.smoothscale(self.img[2], self.imgScale)
        self.ObstacleRect = self.Obstacle.get_rect() #setting the bottom mid to a specific place dictated by start positions above
        self.ObstacleRect.midbottom = (x,y)

        self.randInt = random.randint(0, len(self.img)-1)
        self.obstacleMove = False

        

        pass
    def draw(self, screen):
        
        screen.blit(self.Obstacle, self.ObstacleRect)
        # pg.draw.rect(surface=screen, color="lightblue", rect=self.ObstacleRect, width= 2)

        # screen.blit(self.img[2], self.rect)

    def update(self):
        self.randintx = random.randint(player_xPos, width*2)
        self.imgIndex = random.randint(0,len(self.img)-1)

        #use this for l=platform logic in player class
        self.platformObsList = [0,]
        if self.imgIndex in self.platformObsList:
            # print("yes in list")
            player.platformBool = True

        # self.randinty = random.randint(height*2/4, height*2/3) #use to adjust the obstacles height but not now

        if self.obstacleMove == True: #this is changed by player input K_d
            self.ObstacleRect.right -= abs(player.dx)
            # self.ObstacleRect.bottom = player_yPos

        if self.ObstacleRect.right <= 0:
            # self.ObstacleRect.bottom = player_yPos
            # self.imgIndex += 1#self.randInt
            # if self.imgIndex >= len(self.img):
            #     self.imgIndex = 0
            self.change_image(self.imgIndex)
            self.ObstacleRect.left = width + self.randintx #random pos of respawn
     
    def update_image(self, index):
        self.imgIndex = index
        self.imgSelect = self.img[self.imgIndex]

        # Scale the selected image
        # scaleNum = 1/10
        self.imgSize = self.imgSelect.get_size()
        new_width = int(self.imgSize[0] * self.scaleNum)
        new_height = int(self.imgSize[1] * self.scaleNum)
        self.imgScale = (new_width, new_height)

        # scale and also update the rect dimensions based on new loaded image
        self.Obstacle = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.ObstacleRect = self.Obstacle.get_rect()
        self.ObstacleRect.midbottom = (width, self.y)
        
    def change_image(self, new_index):
        # change image and draw new rect with correct dimensions no squashing or stretch
        if 0 <= new_index < len(self.img):
            self.update_image(new_index)
        
class SkateParts():
    def __init__(self, imgIndexOG, itemCount, scaleNum = 1/10, staticMotion=False ):
        self.imgIndexOG = imgIndexOG
        self.itemCountOG = itemCount
        self.scaleNum = scaleNum
        self.angle = 0
        self.staticMotion = staticMotion
        self.reset()

    def reset(self):
        self.img = [
            pg.image.load("graphics/wheel.png").convert_alpha(),
            pg.image.load("graphics/wheelPack.png").convert_alpha(),
            pg.image.load("graphics/trucks.png").convert_alpha(),
            pg.image.load("graphics/truckPack.png").convert_alpha(),
            pg.image.load("graphics/bearings.png").convert_alpha(),
            pg.image.load("graphics/boardDeck.png").convert_alpha(),
            pg.image.load("graphics/boardSideViewL.png").convert_alpha(),
            pg.image.load("graphics/boardGripTape.png").convert_alpha(),
            pg.image.load("graphics/completeDeck.png").convert_alpha(),
            pg.image.load("graphics/boardSideViewR.png").convert_alpha()

        ]

        self.imgIndex = self.imgIndexOG
        self.imgSelect = self.img[self.imgIndex]

        # self.scaleNum = 1/10 #change this to scale original image
        # self.imgSize = self.imgSelect.get_size() #(240, 300)
        # self.imgScale = (self.imgSize[0]*scaleNum, self.imgSize[1]*scaleNum)

        self.imgSize = self.imgSelect.get_size()  # Original image size
        new_width = int(self.imgSize[0] * self.scaleNum)
        new_height = int(self.imgSize[1] * self.scaleNum)
        self.imgScale = (new_width, new_height)
       
        self.surf = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        # self.surf = pg.transform.rotate(self.surf, self.angle)
        # self.Obstacle = pg.transform.smoothscale(self.img[2], self.imgScale)
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

        pass

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

        
            
    def update(self):
        self.trackItem()
        if self.spawnItem == True:
            if self.staticMotion == False:
                self.rect.x -= player.dx #adjust this to a global movement to remove wiggle
            
            self.randintx = random.randint(player_xPos, width)
            self.randinty = random.randint(int(height*1/6), int(height*2/6))

            if self.rect.right < -200:
                self.rect.left = width*self.randInt + self.randintx #to give more sense of randomness
                self.rect.top = self.randinty
                # self.spawnNewTrigger = True
                # print("in skateparts update:",self.randinty)

            # #later change this section to only save once the game has ended then update the endScreen()
            # self.lines = str(self.finalItemcount)
            # if gameActive == True:
            #     with open(f"saveParts{self.imgIndex}.txt", mode="w", encoding="utf-8") as f:
            #         self.lines = f.writelines(self.lines)
            
            self.draw()

    def rotateItem(self):
        self.rotateCount +=1
        if self.rotateBool == True:
            if self.rotateCount >=5:
                self.angle += 90 #for some reason this also makes the image change size if smaller? BUG
                self.currPosRot = self.rect.midbottom
                rotatedSurf = pg.transform.rotate(self.imgSelect, self.angle)  #rotate og image so doesn't get blurry
                self.surf = pg.transform.smoothscale(rotatedSurf, self.imgScale)  #scale image again
                self.rect = self.surf.get_rect()
                self.rect.midbottom = self.currPosRot
                self.rotateCount = 0
    
    def flipItem(self):
        self.flipCount +=1        
        if self.flipBool == True:
            if self.flipCount >=self.flipTimeNum*2:
                self.flip_x = 1
                self.flipCount = 0
            elif self.flipCount >= self.flipTimeNum:
                self.flip_x = 0    
            self.currPosRot = self.rect.midbottom
            rotatedSurf = pg.transform.flip(self.imgSelect, self.flip_x, 0)  #rotate og image so doesn't get blurry
            self.surf = pg.transform.smoothscale(rotatedSurf, self.imgScale)  #scale image again
            self.rect = self.surf.get_rect()
            self.rect.midbottom = self.currPosRot                         

    def draw(self):
        if self.rotateBool == True:
            self.rotateItem()
        elif self.flipBool == True:
            self.flipItem()
        screen.blit(self.surf, self.rect)
        # pg.draw.rect(surface=screen, color="red", rect=self.rect, width= 2)

class Cash():
    def __init__(self, staticMove = False):
        self.staticMove = staticMove
        self.reset()

    def reset(self):
        self.imgOG = pg.image.load("graphics/cash.png").convert_alpha()

        self.x = width*1/2
        self.y = height*2/3
        
        self.width = self.imgOG.get_width()
        self.height = self.imgOG.get_height()

        self.scaleNum = 1/10

        self.newWidth = int(self.width *  self.scaleNum)
        self.newHeight = int(self.height * self.scaleNum) #no floats
        self.imgScale = (self.newWidth, self.newHeight)

        self.img = pg.transform.smoothscale(self.imgOG, self.imgScale)

        self.rect = self.img.get_rect()
        self.rect.midbottom = (self.x, self.y)

        self.count = 0
        self.angle = 0
        self.rstBool = False
        self.cashcount = 0
    
    def draw(self):

        "logic for rotating cash need code from Dominic"
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
        self.finalCashText = textFont1.render(f'${self.cashcount}', True, ("green"))
        self.finalCashRect = self.finalCashText.get_rect(center = (350, height-260))
        screen.blit(self.finalCashText, self.finalCashRect)
    
    def update(self):
        if self.staticMove == False:
            self.rect.x -= player.dx
            self.randintx = random.randint(player_xPos, width)
            self.randinty = random.randint(int(height*2/4), int(height*2/3))
            
            if self.rect.colliderect(player.playerRect.x +player.dx, player.playerRect.y, player.playerRect.w, player.playerRect.h): #add prediction collision with dx
                cashSound.play() #delay in sound, clip audio
                self.rect.left = width + self.randintx
                self.rect.bottom = self.randinty
                self.cashcount += 1 #add a cash count and load to text after some amount
            if self.rect.right < 0:
                self.rect.left = width + self.randintx
                self.rect.bottom = self.randinty
            
        self.draw()
        
class SpecialItemDisp():
    def __init__(self, specialItemList):
        spawnSpecialItemList
        self.conStartPosx = 0
        self.conStartPosy = 0
        self.winButtonAnimationCounter = 0
        self.animationLimitNum = 50
        self.reset()
    def reset(self):
        cashDisp.rect.center = (width*1/6, 100)
        wheelPack.rect.center = (width*2/6, 100)
        truckPack.rect.center = (width*3/6, 100)
        bearingsDisp.rect.center = (width*4/6, 100)
        boardDeckDisp.rect.center = (width*5/6, 100)

        self.cashCount = textFont1.render(f': ${cash.cashcount}', True, ("black"))
        self.cashCountRect = self.cashCount.get_rect(center = (width*1/6 +80, 100))

        self.wheelCount = textFont1.render(f': {wheel.finalItemcount}/4', True, ("black"))
        self.wheelCountRect = self.wheelCount.get_rect(center = (width*2/6 +80, 100))

        self.truckCount = textFont1.render(f': {trucks.finalItemcount}/2', True, ("black"))
        self.truckCountRect = self.truckCount.get_rect(center = (width*3/6 +80, 100))

        self.bearingCount = textFont1.render(f': {bearings.finalItemcount}/8', True, ("black"))
        self.bearingCountRect = self.bearingCount.get_rect(center = (width*4/6 +80, 100))

        self.boardDeckCount = textFont1.render(f': {boardDeck.finalItemcount}/1', True, ("black"))
        self.boardCountRect = self.boardDeckCount.get_rect(center = (width*5/6 +80, 100))

        self.winTextSurf = textFont1.render('You Win!!!', True, ("green"))
        self.winTextRect = self.winTextSurf.get_rect(center = (width/2 , 200))


        # self.conStartPosx = 0
        # self.conStartPosy = 0

        # self.imgScaleNum = 1/2
        self.imgConfetti = pg.image.load("graphics/winConfetti.png").convert_alpha()
        # self.imgConfettiSize = self.imgConfetti.get_size()
        # self.imgConfettiScaled = (self.imgConfettiSize[0]*self.imgScaleNum,self.imgConfettiSize[1]*self.imgScaleNum)
        # self.imgSurf = pg.transform.smoothscale(self.imgConfetti, self.imgConfettiScaled)

        self.imgRect = self.imgConfetti.get_rect()
        


        pass


    def drawConfetti(self):
        self.conStartPosy += 1
        # print(self.conStartPosy)
        if self.conStartPosy >= self.imgConfetti.get_height()-300:
            self.conStartPosy = 0
        screen.blit(self.imgConfetti, (self.conStartPosx , self.conStartPosy, self.imgRect.w, self.imgRect.h))
        screen.blit(self.imgConfetti, (self.conStartPosx , self.conStartPosy- self.imgConfetti.get_height()+300))


    def update(self):
        
        wheelPack.update()
        truckPack.update()
        bearingsDisp.update()
        boardDeckDisp.update()
        cashDisp.update()

        screen.blit(self.wheelCount, self.wheelCountRect)
        screen.blit(self.truckCount, self.truckCountRect)
        screen.blit(self.bearingCount, self.bearingCountRect)
        screen.blit(self.boardDeckCount, self.boardCountRect)
        screen.blit(self.cashCount, self.cashCountRect)

        # self.winText = endScreen.blinkText("You Win!!!", "black", "green")
        # screen.blit(self.winTextSurf, self.winTextRect)
      
        # self.winButtonAnimationCounter += 1            
        # if self.winButtonAnimationCounter > self.animationLimitNum*2:
        #     youWinButton.update()
        #     self.winButtonAnimationCounter = self.animationLimitNum #this fixed it to be smoother
        # elif self.winButtonAnimationCounter > self.animationLimitNum*1:
        #     youWinButtonB.update()
        # elif self.winButtonAnimationCounter > 0:
        #     youWinButton.update()
        # else:
        #     pass

        #if win condition is met
        if completeDeck.itemCount == 0:
            youWinButton.update()
            self.drawConfetti()
            # print("you win!!!")

        self.reset()
        pass



#creating character rects
# playerRect = playerSurf.get_rect(midbottom=(player_xPos, player_yPos))
enemyRect = enemy1.get_rect(midbottom=(player_xPos1, player_yPos1))

#draw ref rect
plat1 = pg.Rect(0,0, 258, 50)
plat1Surf = pg.Surface((plat1.w, plat1.h))
plat1Surf.fill((255,255,255))


#timers and ticks
start_ticks = pg.time.get_ticks()

#Score
def displayScore():
    global currentTime, cT
    cT = (pg.time.get_ticks() - start_ticks)
    currentTime = int((cT)/1000)
    scoreSurf = textFont1.render(f'Time: {currentTime}s', True, (255,255,255))
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
    enemyRect.x = width 
    obstacle1.ObstacleRect.x = width
    NPC1.NPC1Rect.x = width
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
    # pg.event.clear(eventtype=pg.KEYUP) #not working

#---------------------------------------
#INSTANTIATING CLASSES:
sky = World(0, 0.25, 0)
world = World(1,0,0)
bgPowerLines = World(2,0,0)
bgBirds = World(3,0.55,0)

board = Skateboard()
player = Player(player_xPos, player_yPos)
NPC1 = NPC((width-400)/2,524)
endScreen = EndScreen()
mainMenu = MainMenu()

playButton = Button(width/2, height/2, 0, (1/6))
playAgainButton = Button(width/2, height/2, 5, (1/3))
controlsButton = Button(250, height-200, 1, (1/4))
menuButton = Button(250, height-200, 2, (1/6))
objectiveButton = Button(width-250, height-200, 4, (1/4))
youWinButton = Button(width/2, 200, 6, (1/4))
youWinButtonY = Button(width/2, 200, 7, (1/4))
youWinButtonB = Button(width/2, 200, 8, (1/4))


obstacle1 = Obstacles(width/2, player_yPos)
cash = Cash()
cashDisp = Cash(True)

#skateparts
wheel = SkateParts(0, 4)
wheelPack = SkateParts(1, 1, 1/18, True)
trucks = SkateParts(2, 2) 
truckPack = SkateParts(3,1, 1/18, True)
bearings = SkateParts(4, 8)
bearingsDisp = SkateParts(4, 1, 1/18, True)
boardDeck = SkateParts(5, 1, 1/14)
boardDeckDisp = SkateParts(5, 1, 1/18, True)
boardSideLDisp = SkateParts(6, 1, 1/8, True)
boardSideRDisp = SkateParts(9, 1, 1/8, True)
boardGripTapeDisp = SkateParts(7, 1, 1/8, True)
completeDeckDisp = SkateParts(8, 1, 1/8, True)
completeDeck = SkateParts(8, 1)



specialItemSpawnCounter = 0 #used to make a timer to spawn them more sparely
spawnSpecialItemBool = True
spawnSpecialItemList = [wheel,
                        trucks,
                        bearings,
                        boardDeck
                        ]

#to display tracking during game on screen
specialItemDisp = SpecialItemDisp(spawnSpecialItemList)

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


#DEFINING GAME FUNCTIONS:


#Level Handling not in use since we will only have one continous level for this iteration

# endScreen.endBool = True #here for testing purposes
while running:
    #so all functions have access to keys presed
    keys = pg.key.get_pressed()

    #ENTER MAIN MENU
    
    # if mainMenu.menuBool == True:
      
    if mainMenu.menuBool == True and endScreen.endBool == False:
        mainMenu.update() 
    elif mainMenu.menuBool == False and endScreen.endBool == False:
        gameActive = True
    else:
        pass
        

    

    for event in pg.event.get():

        if event.type == pg.QUIT:
            pg.quit() #opposite of pg init
            sys.exit(0) #stops while loop and ends cleanly
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit(0) 
            if event.key == pg.K_m:
                
                #if the menu key is hit then reset all characters and obstacles
                grindLandSlide.stop()
                rollingSound.stop()
                controlsButton.mouseBool = False
                mainMenu.menuBool = True
                endScreen.endBool = False
                gameActive = False
                obstacle1.ObstacleRect.x = width
                player.reset(player_xPos,player_yPos)
                # pg.event.clear() #not working needs to clear key input so not movement happens after
                # mainMenu.update()
            # if event.type == pg.KEYDOWN:
            #     if event.key == pg.K_d:
            #         world.bgMove = True
            pass

        #PASS EVENTS TO OTHER OBJECTS IN CLASSES:
        playButton.playerInput(event)
        playAgainButton.playerInput(event)
        controlsButton.playerInput(event)
        menuButton.playerInput(event)
        objectiveButton.playerInput(event)

        if gameActive == True:
            pass
              
        else:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    # resetALL()          
                    "all the below moved to endScreen() and mainMenu()"          
                    # #RESETTING CHARACTER POSITIONS AND ITERERATIONS:
                    # start_ticks = pg.time.get_ticks()
                    # current_ticks = 0
                    # # player.playerRect.x  = player_xPos
                    # # player.readyJumpBool = False
                    # # player.dx = 0
                    # enemyRect.x = width 
                    # obstacle1.ObstacleRect.x = width
                    # NPC1.NPC1Rect.x = width
                    # mainMenu.menuBool = False
                    # gameActive = True
                    # # sky.reset()
                    # # world.reset()
                    # player.reset(player_xPos,player_yPos)
                    # cash.reset()
                    # # pg.event.clear(eventtype=pg.KEYUP) #not working
                    pass
                pass

    #Do the following only if the game is active
    if gameActive == True:

        #---------------------------------------

        #BLITTING CHARACTERS, BACKGROUND, AND OBJECTS ON THE SCREEN

        #background and text
        sky.update()
        bgBirds.update()
        world.update()
        bgPowerLines.update()  
        obstacle1.update()
        # screen.fill((0,0,0)) #temporary so to test drawings
        sky.draw(screen)
        bgBirds.draw(screen)
        world.draw(screen)
        NPC1.update()
        # board.update()
        bgPowerLines.draw(screen) #placed after npc to hide him behind the power lines
        
        specialItemDisp.update()

        obstacle1.draw(screen)

        #randomly spawn special items so it feels more random and unique    
        specialItemSpawnInt = random.randint(0, len(spawnSpecialItemList)-1)
        if spawnSpecialItemBool == True:
            spawnSpecialItemList[specialItemSpawnInt].update()
            tempInt = specialItemSpawnInt
            spawnSpecialItemBool = False
        else:
            specialItemSpawnCounter += 1
            # print(specialItemSpawnCounter)
            # print(spawnSpecialItemList[tempInt].itemCount)
            spawnSpecialItemList[tempInt].update()
            # print(boardDeck.itemCountOG, boardDeck.finalItemcount, boardDeck.itemCount)
            if spawnSpecialItemList[tempInt].spawnItem == False:
                # print("last item collected of this one")
                # spawnSpecialItemList.remove(spawnSpecialItemList[tempInt])
                spawnSpecialItemBool = True
            if spawnSpecialItemList[tempInt].rect.right <0: #spawnSpecialItemList[tempInt].spawnNewTrigger == True:
                # print("inelse spawn")
                # print(specialItemSpawnCounter)
                if specialItemSpawnCounter >= 1000: #make higher for more sparse spawning

                    spawnSpecialItemList[specialItemSpawnInt].update()
                    spawnSpecialItemBool = True
                    specialItemSpawnCounter = 0
                    # spawnSpecialItemList[tempInt].spawnNewTrigger = False
                    # if spawnSpecialItemList[specialItemSpawnInt].rect.right < 0:
                    #     spawnSpecialItemList[specialItemSpawnInt].update()
        
        # print(totalSpecialPartsList())
        # completeDeck.rect.bottom -= 50
        
        if finalSpecialItemCount() == totalSpecialPartsList(): #should be 15 items
            print("Complete Deck time!")
            completeDeck.update()
        

            # if completeDeck.itemCount == 0:
            #     print("You Win!!!")
            #     "create winning screen or place something on the screen so you can keep getting cash"
            #     pass
            # pass
                

        cash.update()
        # wheel.update()
        # wheelPack.update()
        # trucks.update()
        # bearings.update()
     
        # board.draw(screen)
        
        # player.playerInput()
        # player.animation()
        player.update()
        
        # NPC1.update()

        #display score
        displayScore()


        #LOSE CONDITION:    
        if player.loseConditionBool == True:
            # print ("game false")
            gameActive = False
            endScreen.endBool = True


    else: #if game is not active do this below
        if endScreen.endBool == True:
            endScreen.update()  
        pass
                    
    #refreshes the screen with a frame rate of 60Hz
    # pg.display.update() #used for updating certain sections only here it is not needed
    pg.display.flip()
    clock.tick(60)