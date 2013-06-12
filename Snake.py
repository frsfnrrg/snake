# -*- coding: utf-8 -*-
import pygame,os
from pygame.locals import *

from snakeCode.constants import *
from snakeCode.colors import GUIColors
from snakeCode.button import button# if the menu system is perfected, this will not be neccessary
from snakeCode.menu import SelectorMenu,SuperMenu, ListMenu
from snakeCode.counter import counter
from snakeCode.highscores import highscores
from snakeCode.textbox import textbox

from math import floor as Floor, ceil as Ceiling

from snakeCode.level import level

# v1: basic playability
# v2: choices and other screens
# v3: get classy
# v4 themes, menus

# List
#v1   basic functionality - it moves, it eats, it crashes, it leaves
#v1.1 win and lose, monocolor screens, with wait
#v1.2 edge wrapping works now - can play any standard map
#v1.3 optimizations - instead of redrawing everything, now circa
#     3% of before- from 60% to 1.7 % CPU. No more lag!!!
#v1.4 win, lose screens are working
#v1.5 cleaned up code- main loop has MODE now, pause/new/quit
#     buttons work, level choice works, only speed control left
#     to do now
#
#v2   Buttons work now, button code cleaned up, new speed system
#v2.1 rounded corners for messages, now loads field as image also -
#     faster rendering - and PATH constant used
#v2.2 added highscores, options, and better win message
#v2.3 fixed highscore bug, redid colors and ported colors to a new file
#v2.4 the snake has its own class: function names and variables
#     have been better named, seperate files for Snake and the constants
#     XSIZE,YSIZE,FIELDS, folder made to organize: snakeCode,levels
#     a script has been made to easy-launch
#v2.5 the field class is finished: a better win animation exists, and
#     updating the snake has been cleaned up: it works correctly now!
#     global UPDATE,UPDATE=True has been replaced by self.update = True
#v3   PATH constant removed: it did nothing anyway. Tail remained bug
#     fixed. A cutscene persistance bug was fixed. Game class created.
#     Menu class create. Speed now is four discrete options. Theme
#     implemented, adjusting color class. Menus and Options working:
#     Mode option to be implemented later. No bugs known of :-)
#v3.1 Mode options. No bugs found yet. Levelset mode implemented.
#     Partial level file redesign. Counter and Highscore classes
#     created. Two highscore files, one per mode. Cleaned up some stuff.
#v3.2 Revamped menu systen; created supermenu class; took almost all the
#     menu work away from Snake.py. The menu system should now be very
#     easily extendable without much work - just init and handle the
#     features added. Added Worm and Gray color themes for the field.
#     Created Numbers levelset. Main file size went down!
#v3.3 Created textbox class. Fixed some bugs. Create a listmenu class,
#     to select levels graphically, and made the Object and Menu classes
#     to give functions whilst saving space.
#v3.4 Created a level class, so playing a single level can be ported easily
#     for a leveleditor.
#v4   We now have a level editor! Squashed some bugs...

# TODO
# v4.1 -> IDK. opponent snakes option w/ better highscores?
#         Remove the 22.786 s/166.067 s spent on pygame.display.flipping?
#         Profiling reveals this as the only avoidable time other than
#         .blit (at 0.293 s / 166.067 s), it is nothing

# NOTE Only use self.update = True were something is being drawn/blitted -
# Only put it where a change (ex. draw.rect) has been made in the immediate function

# 4 Speeds used: note sqrt2
#                   FAST, SPEEDY,  MEDIUM, SLOW
# in bps             20     14       10     7
# fps                60     56       60     56
# tick modulo        3      4        6      8

#Controls:
#Home, End - speed
#Page up, Page down - level(set) change
#Up/Down/Right/Left Arrows - snake controls
#N - restart
#R - reload
#P, Space - pause
#Q,X,Escape - quit

class game():

# ------------------------------------------------- INIT ----------------------------------------------------------------------------------


    def __init__(self):

        # Create Window
        pygame.init()
        windowx = 10 * XSIZE * 2
        windowy = (10 * YSIZE + 20) * 2
        self.screen = pygame.display.set_mode((windowx,windowy), 0,32)
        pygame.display.set_caption('Snake')

        self.loadOptions()# load options

        # set the colors; this must be done before messages, after options
        self.colors = GUIColors()

        # list of displayable messages. WIN is the one that changes
        self.messages = {"NEW":[["Time to Play","Controls are arrow keys. Goal: Eat food, then leave.",
        "Press an arrow key to begin."],self.colors.begin],
        "WIN":[["You Won!","","Press an arrow key to play again."],self.colors.win],
        "WALL":[["Collision","Eating walls is bad for the fangs. (And walls taste disgusting anyway.)",
        "Press an arrow key to try again."],self.colors.collide],
        "SELF":[["Collision","Don't eat yourself!","Press an arrow key to try again."],self.colors.collide],
        "EXIT":[["Still hungry","Satisfy your ravenous appetite BEFORE trying to leave.",
        "Press an arrow key to eat some more."],self.colors.collide],
        "PAUSE":[["Paused","","Press SPACE to continue"],self.colors.paused],
        "GAMEOVER":[["Game Over.","","Press an arrow key to play again."], self.colors.gameover]}# changed when setting a new record

        # Draw and init the buttons
        self.loadButtons()
        self.menu.remoteSet([0], {7:3,10:2,14:1,20:0}[self.speed])
        self.menu.remoteSet([1], self.gametype)# THIS MAY OR MAY NOT WORK
        self.menu.remoteSet([2], {"default":0,"inverted":1,"gray":2,"worm":3}[self.colormode])

        self.highscores = highscores()# load highscores

# ------------------------------------------------- INIT ----------------------------------------------------------------------------------
# ---------------------------------------------- MAIN LOOP --------------------------------------------------------------------------------

    def run(self):
        # but don't jog
        self.mode,tick = 2,0# start ready to begin
        self.levelreached = 0# how far one is on the level set. 0 is at the first level
        self.loadLevel()# load the level

        status = "NEW"# This is the message type that is to be displayed
        self.update = True

        self.cheat = False# if one uses 'c' to get more lives, no highscores will be set
        self.snakelocked = False# when you click on the field, snakelock turns on, and
        # the old snake disappears temporarily

        self.loadGameScreen()# draw the field, and the header
        mcover = self.drawMessage(status)# the rect the message drawing covers
        # Options
        self.optionsEnabled = False# whether or not options were being used at the time,
        # MAIN LOOP
        smileyclock = pygame.time.Clock()# :-)
        while True:
            smileyclock.tick(self.L.getFPS())# ~60 fps

            for event in pygame.event.get():#Quit Check
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:#Keyboard
                    # QUIT
                    if event.key == K_q or event.key == K_ESCAPE:
                        return
                    if event.key == K_HOME:# increment SPEED
                        self.incSpeed()# records change in maximum
                    if event.key == K_END:# decrement SPEED
                        self.decSpeed()
                    if event.key == K_c:# cheat for higher level access until leveleditor appears
                        self.counters[1].add(10)
                        self.updateButtons(-2)
                        self.cheat = True
                    if event.key == K_n:# New game
                        status = "NEW"
                        if self.gametype == 1:
                            self.levelreached = 0
                        self.mode = 2
                        self.loadLevel()
                        self.loadGameScreen()
                        mcover = self.drawMessage(status)

                    # PLAY
                    if self.mode == 0:
                        # Move
                        if event.key == K_UP:# Key and avoid backwards
                            self.L.F.S.addDirection((0,-1))
                        if event.key == K_RIGHT:
                            self.L.F.S.addDirection((1,0))
                        if event.key == K_DOWN:
                            self.L.F.S.addDirection((0,1))
                        if event.key == K_LEFT:
                            self.L.F.S.addDirection((-1,0))

                        if event.key == K_SPACE or event.key == K_p:# Pause
                            self.mode = 1
                            status = "PAUSE"
                            mcover = self.drawMessage(status)

                    # PAUSED
                    elif self.mode == 1:
                        # unpause
                        if event.key == K_SPACE or event.key == K_p:
                            self.updateButtons(1)
                            self.partialRedraw(mcover)
                            self.undrawOptions()
                            self.mode = 0

                    # NEW GAME
                    elif self.mode == 2:

                        # Begin; direction is set in the if iff successful. it comes after (which key?)
                        if event.key == K_UP and self.L.F.S.startDirection((0,-1)) == True:
                            self.start(mcover)

                        if event.key == K_RIGHT and self.L.F.S.startDirection((1,0)) == True:
                            self.start(mcover)

                        if event.key == K_DOWN and self.L.F.S.startDirection((0,1)) == True:
                            self.start(mcover)

                        if event.key == K_LEFT and self.L.F.S.startDirection((-1,0)) == True:
                            self.start(mcover)

                        # field options
                        if event.key == K_r: # Reload: very useful if running leveleditor and this simultaneously
                            status = "NEW"
                            if self.gametype == 1:
                                self.levelreached = 0
                            self.undrawOptions()
                            self.loadLevel()
                            self.loadGameScreen()
                            mcover = self.drawMessage(status)

                        if event.key == K_PAGEUP:# inc level
                            self.incField()
                            mcover = self.drawMessage(status)

                        if event.key == K_PAGEDOWN:# dec level
                            self.decField()
                            mcover = self.drawMessage(status)

                # GET CLICKHAPPY!!
                elif event.type == MOUSEBUTTONDOWN:
                    self.click(True)
                elif event.type == MOUSEBUTTONUP:

                    B = self.click(False)# B stands for ... button

                    # When pressing the OPTIONS, if it is paused, pause continues and options are selected
                    # if it is nongame, is stays nongame, and options are selected
                    # if it is gametime, it is paused, and options are selected

                    if B == "OPTIONS" and self.optionsEnabled == False:
                        self.drawOptions() #
                        if self.mode == 0: # Pause the game if accessing the options while snake is in motion
                            B = "PAUSE"
                    elif B == "OPTIONS" and self.optionsEnabled == True:# the elif is very important ...
                        #lest you just undo yourself. drawOptions sets optionsEnabled true
                        self.undrawOptions()

                    if B  in ("FAST","SPEEDY","RELAXED","SLOW"):
                        self.speed = {"FAST":20,"SPEEDY":14,"RELAXED":10,"SLOW":7}[B]
                        if self.maxSpeed < self.speed:
                            self.maxSpeed = self.speed
                        self.L.setSpeed(self.speed)

                        self.updateOptions()# write preferences to file

                    if B == "LEVELSELECT.>>":
                        self.incField()
                        status = "NEW"
                        mcover = self.drawMessage(status)
                        if self.gametype == 1:
                            self.levelreached = 0
                        self.mode = 2
                    if B == "LEVELSELECT.<<":
                        self.decField()
                        status = "NEW"
                        mcover = self.drawMessage(status)
                        if self.gametype == 1:
                            self.levelreached = 0
                        self.mode = 2

                    if B in ("DEFAULT","INVERTED", "GRAY","WORM"):
                        self.colormode = B.lower()
                        self.L.setColors(self.colormode)

                        self.partialRedraw((0,0,XSIZE*20,YSIZE*20))
                        mcover = self.drawMessage(status)
                        self.drawOptions()
                        self.updateOptions()# write preferences to file

                    if B in ("INDIVIDUAL","LEVELSET"):
                        if B == "INDIVIDUAL":
                            self.gametype = 0
                        if B == "LEVELSET":
                            self.gametype = 1
                        status = "NEW"
                        self.mode = 2
                        self.undrawOptions()
                        self.loadLevel()
                        self.loadGameScreen()
                        mcover = self.drawMessage(status)
                        self.updateOptions()

                    if B == "QUIT":# leave
                        return

                    if B == "NEW":
                        status = "NEW"
                        if self.gametype == 1:
                            self.levelreached = 0
                        self.loadLevel()
                        self.loadGameScreen()
                        mcover = self.drawMessage(status)
                        self.mode = 2

                    if B == "PAUSE":
                        if self.mode == 0:
                            self.mode = 1
                            status = "PAUSE"
                            mcover = self.drawMessage(status)
                        elif self.mode == 1:
                            self.mode = 0
                            self.partialRedraw(mcover)
                            self.undrawOptions()

                    # Change field
                    if B == "F_INC" and MODE == 2:
                        self.incField()
                        mcover = self.drawMessage(status)
                    if B == "F_DEC" and MODE == 2:
                        self.decField()
                        mcover = self.drawMessage(status)
                    # change speed
                    if B == "S_INC":
                        self.incSpeed()
                    if B == "S_DEC":
                        self.decSpeed()

            # UPDATE

            if self.mode == 0:# Tick only matters while playing/anim-ing anyway
                r, s, moved = self.L.update()
                self.DrawSet(r)
                if s != None:
                    status = s

                # Move Counter
                if self.gametype == 0 and s == None and moved == True:
                    if int(self.counters[0]) == 0:
                        self.counters[0].reset(1)# reset move counter
                    else:
                        self.counters[0].add(1)
                    self.updateButtons(-2)# draw the move counter

                if s == "WIN":
                    if self.gametype == 0:
                        record = self.highscores.updateIndividual(self.maxSpeed,self.fieldnumber,int(self.counters[0]))
                        if record == int(self.counters[0]):# reached or broke record
                            self.messages["WIN"][0][0] = "Awesome!"# TODO replace this with a status => "RECORD"
                            self.messages["WIN"][1] = self.colors.record
                        else:
                            self.messages["WIN"][0][0] = "You Won!"
                            self.messages["WIN"][1] = self.colors.win
                        self.messages[status][0][1] = str(int(self.counters[0]))+" moves at speed "+str(self.maxSpeed)+". Record: "+str(record)
                    elif self.gametype == 1:
                        if self.levelreached == self.levelsetsize - 1:
                            record = self.highscores.updateLevelset(self.maxSpeed, self.levelsetnumber, self.levelreached,self.cheat)
                            self.messages["WIN"][0][0] = "Awesome!"
                            self.messages["WIN"][0][1] = "You have won! Yay!"
                            self.messages["WIN"][1] = self.colors.record
                            self.levelreached = 0
                            self.counters[1].reset(SNAKE_LIVES)

                            #self.updateButtons(-2)# this is called anyway
                        else:
                            self.messages["WIN"][1] = self.colors.win
                            self.messages["WIN"][0][0] = "Congratulations!"
                            self.messages["WIN"][0][1] = "On to the next level..."
                            self.levelreached += 1

                    self.mode,tick = 2, 0
                    self.loadLevel()
                    self.loadGameScreen()
                    mcover = self.drawMessage(status)
                    self.updateButtons(1)
                elif s != None:
                    if self.gametype == 1:# You lose a life
                        self.counters[1].subtract(1)
                        if int(self.counters[1]) == 0:
                            record = self.highscores.updateLevelset(self.maxSpeed, self.levelsetnumber, self.levelreached,self.cheat)
                            status = "GAMEOVER"
                            self.messages["GAMEOVER"][0][1] = "You have reached level " + str(self.levelreached+1) + ". Record: " + str(record+1)
                            self.levelreached = 0
                            self.counters[1].reset(SNAKE_LIVES)
                        self.updateButtons(-2)

                    self.loadLevel()
                    self.mode = 2
                    self.loadGameScreen()

                    mcover = self.drawMessage(status)

            if self.update == True:
                # or could only a section be updated?
                # using sectional display.update(rect1,rect2,rect3....) would be better. use self.rects with the Rect() class of pygame
                pygame.display.flip()
                self.update = False

# ---------------------------------------------- MAIN LOOP --------------------------------------------------------------------------------
# --------------------------------------------- DRAW FIELD --------------------------------------------------------------------------------

    def loadGameScreen(self):
        # Choosing whether to load from image or redraw
        self.partialRedraw((0,0,XSIZE*20, YSIZE*20))

        # Draw the 'Header'
        pygame.draw.rect(self.screen, self.colors.headerrim, (0, YSIZE*10*2, XSIZE*10*2, 2))
        pygame.draw.rect(self.screen, self.colors.header, (0, YSIZE*10*2+2, XSIZE*10*2, 20*2))

        self.updateButtons(-1)# draw all buttons

        self.update = True

    def partialRedraw(self,rect):
        self.DrawSet(self.L.getSections([rect]))

# ---------------------------------------------- BUTTONS ----------------------------------------------------------------------------------

    def loadButtons(self):
        buttonfont = pygame.font.Font(None, 40)

        self.numberbuttons = []
        for i in range(10):
            self.numberbuttons.append(button(str(i), self.colors.numbers, PASSIVE_BUTTON))

        self.buttons = [  # main 5
            button("QUIT", self.colors.quit, PLAIN_BUTTON),# 0
            button("PAUSE", self.colors.pause, PLAIN_BUTTON),# 1
            button("NEW", self.colors.new, PLAIN_BUTTON),# 2
            button("HELP", self.colors.help, PLAIN_BUTTON),# 3
            button("OPTIONS", self.colors.options, LOCK_BUTTON)]#,#4


        # 9999 moves is enough for anyone :-)
        self.counters = [counter(0, 4, "MOVES", self.colors.moves, self.colors),
                        counter(SNAKE_LIVES, 4, "LIVES", self.colors.lives, self.colors)
            ]

        # The indentation pattern is designed to show nesting
        self.menu = SuperMenu(
            [
                (
                    button("SPEED",self.colors.options, LOCK_BUTTON),
                    SelectorMenu([
                        button("FAST", self.colors.fast, ITEM_BUTTON),
                        button("SPEEDY", self.colors.speedy, ITEM_BUTTON),
                        button("RELAXED", self.colors.relaxed, ITEM_BUTTON),
                        button("SLOW", self.colors.slow, ITEM_BUTTON)],
                    self.colors)
                ),

                (
                    button("MODE",self.colors.options, LOCK_BUTTON),
                    SelectorMenu([
                        button("INDIVIDUAL", self.colors.individual, ITEM_BUTTON),
                        button("LEVELSET", self.colors.levelset, ITEM_BUTTON)],
                    self.colors)
                ),

                (
                    button("THEME",self.colors.options, LOCK_BUTTON),
                    SelectorMenu([
                        button("DEFAULT", self.colors.default, ITEM_BUTTON),
                        button("INVERTED", self.colors.inverted, ITEM_BUTTON),
                        button("GRAY", self.colors.graybutton, ITEM_BUTTON),
                        button("WORM", self.colors.worm, ITEM_BUTTON)],
                    self.colors)
                ),

                (
                    button("LEVEL", self.colors.options, LOCK_BUTTON),
                    ListMenu("LEVELSELECT", 320, self.colors.levelselect, self.colors)
                )
            ],
             self.colors)

        #active buttons; set positions
        x = XSIZE*20
        y = YSIZE*20+5
        for b in range(0,5):# 0 -> 4 inclusive
            x -= (self.buttons[b].getsize()[0] + 10)
            self.buttons[b].setpos((x,y))

        mx = 0
        for c in self.counters:
            if mx < c.getlength():
                mx = c.getlength()

        self.counters[0].setpos((mx - self.counters[0].getlength() + 3,y))
        self.counters[1].setpos((mx - self.counters[1].getlength() + 3,y))

        tlength = self.buttons[4].getpos()[0] - 10 - (mx + 13)
        self.namebox = textbox(tlength, self.colors.namebox, self.colors.textboxbg, FIXED_TEXTBOX)
        self.namebox.setpos((mx + 13, y))

        bx,by = self.buttons[4].getpos()# OPTIONS button
        lx = self.buttons[4].getlength()
        mx,my = self.menu.getsize()
        self.menu.setpos(  (bx + lx//2 - mx//2, YSIZE * 20 - my)    )# YSIZE*20 is the top of the 'header'
        self.menu.setbounds(0, XSIZE*20)



    def setOptionsButtons(self, enabled):
        if enabled:
            for k in range(7, 10):
                self.buttons[k].enable()
        else:
            for k in range(7, 10):
                self.buttons[k].disable()

    # UPDATE BUTTONS
    def updateButtons(self,s):
        #using
            #-1=All
            #0,1,2,3,4 for buttons
            #-2 updates countersfieldnumber
            #-3 wipes counters (to switch between)
        # Buttons

        if s in (-1,1):# disable pause
            if self.mode not in (0,1):
                self.buttons[1].disable()
            else:
                self.buttons[1].enable()

        if s >= 0:# draw 1
            self.screen.blit(self.buttons[s].image(),  self.buttons[s].getpos())
        if s == -1:# draw all
            self.Draw(self.namebox)
            for k in range(0, 5):#
                self.screen.blit(self.buttons[k].image(),  self.buttons[k].getpos())

        if s in (-1,-2):# All or counters
            self.Draw(self.counters[self.gametype])

        if s == -3:# clear counters- for switching which one
            pygame.draw.rect(self.screen, self.colors.header, self.counters[self.gametype].getrect())

        self.update = True

    # HANDLE CLICK
    def click(self,state): # if state==true, click down

        pos = pygame.mouse.get_pos()

        retdict = ["QUIT","PAUSE","NEW","HELP","OPTIONS"]

        ret = None
        hit = False
        for k in range(0, len(self.buttons)):# Iterate through all existing buttons;
            c, u = self.buttons[k].click(state,pos)
            if c == True:
                self.updateButtons(k)
            if u == True:
                ret = retdict[k]

        draw, udraw, command = self.menu.click(state, pos)
        self.UndrawSet(udraw)
        self.DrawSet(draw)

        if command != None:
            ret = command

        return ret

    def drawOptions(self):
        #Menu
        self.menu.enable()
        self.DrawSet(self.menu.images())
        # OPTIONS button
        self.buttons[4].hold()
        self.Draw(self.buttons[4])# OPTIONS
        self.optionsEnabled = True

    def undrawOptions(self):
        # Menu
        self.UndrawSet(self.menu.undraw())
        self.menu.disable()# one should always undraw before disabling (disabling mentally closes the submenus)
        # OPTIONS button
        self.optionsEnabled = False
        self.buttons[4].release()
        self.Draw(self.buttons[4])


# ---------------------------------------------- BUTTONS ----------------------------------------------------------------------------------
# -------------------------------------------- MESSAGES -----------------------------------------------------------------------------------

    #def drawMessage(self, message,color):
    def drawMessage(self, status):

        # draw the messages
        a = MEDIUM_FONT.render(self.messages[status][0][0], True, self.messages[status][1])
        b = SMALL_FONT.render(self.messages[status][0][1], True, self.messages[status][1])
        c = SMALL_FONT.render(self.messages[status][0][2], True, self.messages[status][1])
        aS = a.get_size()
        bS = b.get_size()
        cS = c.get_size()

        # find longest text
        l = aS[0]
        if aS[0] < bS[0]:
            l = bS[0]
        if bS[0] < cS[0]:
            l = cS[0]

        # text has 15-15 (x) and 5-7-7-5 (y) buffers
        surface = pygame.Surface((l+30,aS[1]+bS[1]+cS[1]+24),SRCALPHA)
        x,y = surface.get_size()

        # rounded corners, etc ;
        #rad = 50# 50-stylish,20,middle,does not stand out
        rad = 50 # New Font: Junction

        # make this into a function? it could be used for buttons too
        pygame.draw.rect(surface, self.colors.messagebg, (rad,0,x-2*rad,y))
        pygame.draw.rect(surface, self.colors.messagebg, (0,rad,rad,y-2*rad))
        pygame.draw.rect(surface, self.colors.messagebg, (x-rad,rad,rad,y-2*rad))

        pygame.draw.circle(surface, self.colors.messagebg, (x-rad,rad),rad)# alas, 3/4 overlap :-(
        pygame.draw.circle(surface, self.colors.messagebg, (rad,y-rad),rad)
        pygame.draw.circle(surface, self.colors.messagebg, (x-rad,y-rad),rad)
        pygame.draw.circle(surface, self.colors.messagebg, (rad,rad),rad)


        # center surface and draw it
        xrect,yrect = XSIZE*10-int(l/2)-12,YSIZE*10-int((aS[1]+bS[1]+cS[1])/2)-12# 20/2 = 10
        self.screen.blit(surface, (xrect,yrect))

        # Text drawn (centered)
        self.screen.blit(a, (XSIZE*10 - int(aS[0]/2),yrect+5))
        self.screen.blit(b, (XSIZE*10 - int(bS[0]/2),yrect+aS[1]+12))
        self.screen.blit(c, (XSIZE*10 - int(cS[0]/2),yrect+aS[1]+bS[1]+19))

        self.update = True
        # mcover: what area the message obscured, and must be redrawn
        return (xrect,yrect,x,y)

# -------------------------------------------- MESSAGES -----------------------------------------------------------------------------------
# ----------------------------------------------  HIGHSCORES ------------------------------------------------------------------------------

    def updateOptions(self):
        optname = "options.txt"
        open(optname,"w").write(str(self.fieldnumber)+","+str(self.levelsetnumber)+","+str(self.speed)+","+str(self.gametype)+","+self.colormode)

    def loadOptions(self):
               # Load options
        optname = "options.txt"
        if os.path.exists(optname):
            OPTIONS = open(optname,"r")
            o = OPTIONS.read().split(",")
            self.fieldnumber = int(o[0])# 0-999
            self.levelsetnumber = int(o[1])
            self.speed = int(o[2])# 1-99
            self.gametype = int(o[3])# 0 (single levels) or 1 (levelsets)
            self.colormode = o[4]
        else:
            print("Creating options.txt")
            open(optname,"w").write("0,0,20,0,default")
            self.fieldnumber = 0
            self.levelsetnumber = 0
            self.speed = 20
            self.gametype = 0
            self.colormode = "default"
        self.maxSpeed = self.speed
        # load the fields
        self.fields = 0
        while os.path.exists("levels/individual/"+threeDigit(self.fields)+".txt"):
            self.fields += 1

        self.levelsets = 0
        while os.path.exists(LEVELSET_MANIFEST.format(threeDigit(self.levelsets))):
            self.levelsets += 1



# ----------------------------------------------  HIGHSCORES ------------------------------------------------------------------------------
# --------------------------------- CHANGE FUNCTIONS FOR MAIN LOOP ------------------------------------------------------------------------

    def decSpeed(self):
        self.speed = self.L.decSpeed()

        draw = self.menu.remoteSet([0], {7:3,10:2,14:1,20:0}[self.speed])
        self.DrawSet(draw)

        if self.maxSpeed > self.speed:
            self.maxSpeed = self.speed

        self.updateOptions()# maybe needed as of yet

    def incSpeed(self):

        self.speed = self.L.incSpeed()
        draw = self.menu.remoteSet([0], {7:3,10:2,14:1,20:0}[self.speed])
        self.DrawSet(draw)

        self.updateOptions()

    def incField(self):
        if self.gametype == 0:
            self.fieldnumber = (self.fieldnumber + 1)%self.fields
        elif self.gametype == 1:
            self.levelsetnumber = (self.levelsetnumber + 1)%self.levelsets
            self.levelreached = 0
            self.counters[1].reset(SNAKE_LIVES)

        self.updateOptions()
        self.loadLevel()
        self.loadGameScreen()
        if self.optionsEnabled:
            self.drawOptions()

    def decField(self):
        if self.gametype == 0:
            self.fieldnumber = (self.fieldnumber - 1)%self.fields
        elif self.gametype == 1:
            self.levelsetnumber = (self.levelsetnumber - 1)%self.levelsets
            self.levelreached = 0
            self.counters[1].reset(SNAKE_LIVES)
        self.updateOptions()
        self.loadLevel()
        self.loadGameScreen()
        if self.optionsEnabled:
            self.drawOptions()

    def loadLevel(self):
        if self.gametype == 0:
            self.L = level(self.colormode, INDIVIDUAL_LEVEL.format(threeDigit(self.fieldnumber)+".txt"), self.speed)

            draw = self.menu.remoteSet([3], [self.L.F.getname(), self.L.F.getauthor()])
            self.DrawSet(draw)

        if self.gametype == 1:
            data = open(LEVELSET_MANIFEST.format(threeDigit(self.levelsetnumber)), "r").read().split("\n")
            self.levelsetname = data[0]
            self.levelsetauthor = data[1]
            self.levelsetsize = int(data[2])# this iscolorscheme also countable, but is easier to put inthe info

            self.L = level(self.colormode, LEVELSET_LEVEL.format(threeDigit(self.levelsetnumber),threeDigit(self.levelreached)+".txt"), self.speed)

            draw = self.menu.remoteSet([3], [self.levelsetname,  self.levelsetauthor])
            self.DrawSet(draw)


        self.namebox.settext(self.L.F.getname())

    def start(self, mcover):# start a game
        self.mode,self.maxSpeed,tick = 0,self.speed,0
        self.counters[0].reset(0)
        self.updateButtons(1)
        self.partialRedraw(mcover)
        self.undrawOptions()

# --------------------------------- CHANGE FUNCTIONS FOR MAIN LOOP ------------------------------------------------------------------------
# --------------------------------------------- SIMPLE ------------------------------------------------------------------------------------

    def Draw(self,item):# a simple function. pass a button, menu, counter and behold! it draws it
        self.screen.blit(item.image(), item.getpos())
        self.update = True

    def UndrawSet(self, udraw):# takes an array of rects, sent from menu system
        for rect in udraw:
            self.partialRedraw(rect)

    def DrawSet(self, draw):# takes an array of (image, pos) pairs, sent from the menu system
        for img in draw:
            self.screen.blit(img[0], img[1])
        self.update = True


# --------------------------------------------- SIMPLE ------------------------------------------------------------------------------------
# ------------------------------------------- OUT OF CLASS --------------------------------------------------------------------------------

def threeDigit(number):# so it looks cleaner
    return "0"*(3-len(str(number)))+str(number)

# ------------------------------------------- OUT OF CLASS --------------------------------------------------------------------------------
# -------------------------------------------- MAIN CODE ----------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if "-d" in sys.argv:
        import cProfile
        cProfile.run("game().run()", "profile.txt")
        import pstats
        p = pstats.Stats("profile.txt")
        p.sort_stats('time').print_stats(50)
    else:
        SnakeGame = game()
        SnakeGame.run()
    quit()