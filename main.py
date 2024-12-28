import pygame as pg
import sys
import random


#Dev Notes:
# right now it is working push these changes. 12/26/2024
# To Do:
#Add collision detection so that the skater can grind the objects
"Might have to do with the new values. maybe change to integers or add in main menu and other stuff to handle end game stuff"
#Edit the jump height to be a percentage of what it was with floor division


pg.init()
# pg.mixer.init()
print("starting")
# display screen and basic set up
width = 1280 *0.625
height = 720 *0.625
resolution = (width, height)
screen = pg.display.set_mode(resolution, pg.RESIZABLE)
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
# disp_icon = pg.image.load("graphics/HeadofKittyBoardBluntLoyalton.png").convert_alpha()

#place images to respective locations
# pg.display.set_icon(disp_icon) #load it to the display window

#starting positions
player_xPos = 250 *0.625 // 1
player_yPos = 675 *0.625 // 1
player_xPos1 = 1280
player_yPos1 = 675

#setting up booleans
running = True
gameActive = False

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
        self.imgScaled = (self.imgSize[0]*scaleNum *0.625 // 1, self.imgSize[1]*scaleNum *0.625 // 1) #all images should be the same sie or else this wont work
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
            self.bgStartPosx -= abs(player.dx)/6#+self.bgSpeed
            if player.dx == 0:
                self.bgMove = False
        elif self.kMoveBool == True:
            self.bgStartPosx -= self.bgSpeed

        #if the background has fully scrolled off the screen, reset position
        if self.bgStartPosx <= -self.background.get_width():
            self.bgStartPosx = 0

    def draw(self):
        screen.blit(self.background, (self.bgStartPosx, self.bgStartPosy))
        screen.blit(self.background, (self.bgStartPosx+self.background.get_width(), self.bgStartPosy)) #twice for seamless repetition

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
        self.player_TranformedList = []

        for index in range(len(self.img)):
            self.imgSelect = self.ollieImages[index] #self.current_image_index
            self.scaleNum = 1/13 #change this to scale original image
            self.imgSize = self.imgSelect.get_size()  #original image size
            new_width = int(self.imgSize[0] * self.scaleNum)
            new_height = int(self.imgSize[1] * self.scaleNum)
            self.imgScale = (new_width, new_height)
            self.player = pg.transform.smoothscale(self.imgSelect, self.imgScale)
            self.player_TranformedList.append(self.player)

        self.player = self.player_TranformedList[self.current_image_index]

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
                # rollingSound.play(-1)  # Play in loop mode
                pass
            self.playRolling = True #makes it so only sets loop one time
            # rollingSound.set_volume(self.volume/3)
        # elif self.movingLeft == True:
        #     rollingSound.fadeout()
        else:
            if self.playRolling == True:
                # rollingSound.stop()
                pass
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
                self.gravity = -20 #25 UNCOMMENT used to be 25 when resolution was full
                # ollieUpSound.play()
                # ollieUpSound.set_volume(0.5)
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
            # print("collided")
            
            if obstacle1.ObstacleRect.left < self.playerRect.right-25: #adjust num if needed -25 is good
                pass

            elif obstacle1.ObstacleRect.left <= self.playerRect.right:
                "BAIL IN X POS"
                # print("BAIL!!!!!!!!!!!!!!!!!!!!!!!")
                "there may be a condition where this falsely triggers but I think it's ok for now"
                # rollingSound.stop()
                self.dx = 0
                self.loseConditionBool = True
                # print("loseloselose in x dir", self.loseConditionBool)
                "issue: triggered but not ending game" #Resolved was due to elif below was only if
                "ADD BAIL SOUND HERE"
                
                if self.bailBool == False:
                    # rollingSound.set_volume(0.15)
                    # grindLand.play()
                    # boardHitObj.play()
                    # livBailVoice.play()  # Play in loop mode
                    # dorBailVoice.play()
                    pass
                self.bailBool = True #makes it so only sets loop one time
                # livBailVoice.set_volume(self.volume/2)

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
            if obstacle1.ObstacleRect.top+int(40*0.625) > self.playerRect.bottom > obstacle1.ObstacleRect.top and self.grindKeyBool == True: #used to be 20 no 40
                # print("vert")
                # rollingSound.stop()
                "grind enable Vertical range "
                if keys[pg.K_SPACE]:
                    # self.inAirBool = False
                    # ollieUpSound.play()
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
                        # grindLandSlide.play()  # Play in loop mode
                        pass
                    self.grindBool = True #makes it so only sets loop one time
                    # grindLandSlide.set_volume(self.volume)
                # elif self.movingLeft == True:
                #     rollingSound.fadeout()
                else:
                    # print("in else statement")
                    if self.grindBool == True:
                        # grindLandSlide.stop()
                        pass
                    self.grindBool = False
                    # self.inAirBool = False
                
                    # print(self.surf.get_width()*0.25) #=28.25 
                # print("in Vert grind range")
            
            else:
                if self.playerRect.bottom > obstacle1.ObstacleRect.top+int(20*0.625):
                    "TO DO: 11/10/2024"
                    " find a way to register the range that is out of bounds when exiting the grinding if statement above" #resolved
                    # print("Below grind range")

                    if self.playerRect.left+self.surf.get_width()*int(0.25*0.625) < obstacle1.ObstacleRect.right:
                        # print("NOT safe range for exiting grind")
                        self.loseConditionBool = True
                        "ADD BAIL SOUND HERE"
                        if self.bailBool == False:
                            # rollingSound.set_volume(0.15)
                            # grindLand.play()
                            # bailSound.play()
                            # bailSoundTopple.play()
                            # livBailVoice.play()  # Play in loop mode
                            # dorBailVoice.play()
                            pass
                        self.bailBool = True #makes it so only sets loop one time
                        # livBailVoice.set_volume(self.volume/2)
                    else:
                        # print("Out of BAIL range")
                        self.playSound() #play rolling sound after grind logic bug fixed
                        pass

            # else:
            #     "BAIL"
            #     # print("BAIL!!!")
            #     self.loseConditionBool = True
        else:
            # grindLandSlide.stop() #needed so when collision is not happening sound is stopped
            self.grindBool = False
            self.loseConditionBool = False
            pass

        if self.loseConditionBool == True:
            # print("BAIL!!!!!")
            # grindLandSlide.stop()
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
                        # ollieDownSound.play()
                        # ollieDownSound.set_volume(0.5)
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
        new_width = int(self.imgSize[0] * self.scaleNum*0.625 // 1)
        new_height = int(self.imgSize[1] * self.scaleNum*0.625 // 1)
        self.imgScale = (new_width, new_height)

        # scale and also update the rect dimensions based on new loaded image
        self.surf = self.player = pg.transform.smoothscale(self.imgSelect, self.imgScale)
        self.playerRect = self.player.get_rect()

        self.playerRect.midbottom = self.curPosPass#(player_xPos, self.currentPos[1])
        self.draw(self.surf, self.playerRect)

        #temp rect
        self.tempRectx = pg.rect.Rect(self.playerRect[0]+self.tempPosAdj, self.playerRect[1], self.playerRect.w, self.playerRect.h)
        self.tempRectx.bottom = self.playerRect.bottom-self.tempPosAdj

        self.tempRecty = pg.rect.Rect(self.playerRect[0], self.playerRect[1]+self.tempPosAdj, self.playerRect.w, self.playerRect.h)
        self.tempRecty.right = self.playerRect.right-self.tempPosAdj
        self.tempRecty.bottom = self.playerRect.bottom + self.tempPosAdj

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
        self.img_List =[]
        for index in range(len(self.img)):
            self.imgSelect = self.img[index]
            self.scaleNum = 1/6 #change this to scale original image

            self.imgSize = self.imgSelect.get_size()  # Original image size
            new_width = int(self.imgSize[0] * self.scaleNum)
            new_height = int(self.imgSize[1] * self.scaleNum)
            self.imgScale = (new_width *0.625, new_height *0.625)
        
            self.Obstacle = pg.transform.smoothscale(self.imgSelect, self.imgScale)
            self.img_List.append(self.Obstacle)

        self.index = 0
        self.Obstacle = self.img_List[self.index]

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

        self.imgSelect 
        self.Obstacle = self.img_List[index]
        self.ObstacleRect = self.Obstacle.get_rect()
        self.ObstacleRect.midbottom = (width, self.y)
        
    def change_image(self, new_index):
        # change image and draw new rect with correct dimensions no squashing or stretch
        if 0 <= new_index < len(self.img):
            self.update_image(new_index)
  
#instantiate world
sky = World(bg_List[0], 0.25)
world = World(bg_List[1],0)
bgPowerLines = World(bg_List[2],0)
bgBirds = World(bg_List[3],0.55)

player = Player(player_xPos, player_yPos)
# NPC1 = NPC((width-400)/2,524)
# endScreen = EndScreen()
# mainMenu = MainMenu()

# playButton = Button(width/2, height/2, 0, (1/6))
# playAgainButton = Button(width/2, height/2, 5, (1/3))
# controlsButton = Button(250, height-200, 1, (1/4))
# menuButton = Button(250, height-200, 2, (1/6))
# objectiveButton = Button(width-250, height-200, 4, (1/4))
# youWinButton = Button(width/2, 200, 6, (1/4))
# youWinButtonY = Button(width/2, 200, 7, (1/4))
# youWinButtonB = Button(width/2, 200, 8, (1/4))

obstacle1 = Obstacles(width/2, player_yPos)
# cash = Cash()
# cashDisp = Cash(True)

# #skateparts
# wheel = SkateParts(0, 4)
# wheelPack = SkateParts(1, 1, 1/18, True)
# trucks = SkateParts(2, 2) 
# truckPack = SkateParts(3,1, 1/18, True)
# bearings = SkateParts(4, 8)
# bearingsDisp = SkateParts(4, 1, 1/18, True)
# boardDeck = SkateParts(5, 1, 1/14)
# boardDeckDisp = SkateParts(5, 1, 1/18, True)
# boardSideLDisp = SkateParts(6, 1, 1/8, True)
# boardSideRDisp = SkateParts(9, 1, 1/8, True)
# boardGripTapeDisp = SkateParts(7, 1, 1/8, True)
# completeDeckDisp = SkateParts(8, 1, 1/8, True)
# completeDeck = SkateParts(8, 1)

#debugging delete later:
gameActive = True

while running:
    #so all functions have access to keys presed
    keys = pg.key.get_pressed()

    #ENTER MAIN MENU
    
    # if mainMenu.menuBool == True:
    
    # if mainMenu.menuBool == True and endScreen.endBool == False:
    #     mainMenu.update() 
    # elif mainMenu.menuBool == False and endScreen.endBool == False:
    #     gameActive = True
    # else:
    #     pass 

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
                # grindLandSlide.stop()
                # rollingSound.stop()
                # controlsButton.mouseBool = False
                # mainMenu.menuBool = True
                # endScreen.endBool = False
                # gameActive = False #UNCOMMENT
                obstacle1.ObstacleRect.x = width
                player.reset(player_xPos,player_yPos)
            pass

        #PASS EVENTS TO OTHER OBJECTS IN CLASSES:
        # playButton.playerInput(event)
        # playAgainButton.playerInput(event)
        # controlsButton.playerInput(event)
        # menuButton.playerInput(event)
        # objectiveButton.playerInput(event)

        if gameActive == True:
            pass
            
        else:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    # resetALL()          
                    "all the below moved to endScreen() and mainMenu()"          
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

        sky.draw()
        bgBirds.draw()
        world.draw()
        # NPC1.update()
        bgPowerLines.draw() #placed after npc to hide him behind the power lines
        # specialItemDisp.update()
        obstacle1.draw()
        # cash.update()
        player.update()
        # displayScore()

        # #randomly spawn special items so it feels more random and unique    
        # specialItemSpawnInt = random.randint(0, len(spawnSpecialItemList)-1)
        # if spawnSpecialItemBool == True:
        #     spawnSpecialItemList[specialItemSpawnInt].update()
        #     tempInt = specialItemSpawnInt
        #     spawnSpecialItemBool = False
        # else:
        #     specialItemSpawnCounter += 1
        #     spawnSpecialItemList[tempInt].update()
        #     if spawnSpecialItemList[tempInt].spawnItem == False:
        #         spawnSpecialItemBool = True
        #     if spawnSpecialItemList[tempInt].rect.right <0: #spawnSpecialItemList[tempInt].spawnNewTrigger == True:
        #         if specialItemSpawnCounter >= 1000: #make higher for more sparse spawning

        #             spawnSpecialItemList[specialItemSpawnInt].update()
        #             spawnSpecialItemBool = True
        #             specialItemSpawnCounter = 0
        
        # if finalSpecialItemCount() == totalSpecialPartsList(): #should be 15 items
        #     # print("Complete Deck time!")
        #     completeDeck.update()

        #LOSE CONDITION:    
        if player.loseConditionBool == True:
            # print ("game false")
            # gameActive = False
            # endScreen.endBool = True
            pass

    # else: #if game is not active do this below
    #     if endScreen.endBool == True:
    #         endScreen.update()  
    #     pass
                    
    #refreshes the screen with a frame rate of 60Hz
    pg.display.flip()
    clock.tick(60)