# -*- coding: utf-8 -*-
import pygame,os
from pygame.locals import *

from snakeCode.constants import *
from snakeCode.colors import GUIColors as C
from snakeCode.button import button, toolbutton, tributton
from snakeCode.menu import SelectorMenu, SuperMenu, ListMenu, SuperPanel
from snakeCode.counter import counter
from snakeCode.textbox import textbox, inputbox
from snakeCode.level import level
from snakeCode.sidebar import Sidebar
from snakeCode.levelsetscreen import LevelSetScreen

from snakeCode.levelselect import level as LevelSource, getNextOpen as NewAddress, emptyfeed, lslevel as LSLevelSource, createnextlevelset as NextLSet, nextopenlpath as NextOpenLPath, lsi as LevelSetInsert

from math import floor as Floor, ceil as Ceiling

# v0.0: can change levels
# v0.1: added toolbar, main panel, cleaned up stuff.
# v0.2: added an input textbox, cleaned stuff
# v0.3: cleaned up menu system: fixed some bugs:
#       old images are now deleted with a change!
# v1.0: fixed bugs with the menu system:
#       implemented levesets and appropriate gui
#       all original goals set.

# Goals:
# Create a level editor for Snake.py's levels. It should create levels,
# and run them (but only the worked on level): that is for the game itself.
# The level editor should have a text input object for it to give text:
# select on 2click, the all characters are captured. Enter gives info, 2click
# releases.
# main: the field
# right bar: 60 wide, with a selector for type:
# \-------------\--\
# \             \  \
# \             \  \
# \             \  \
# \-------------+--\
# \----------------\
#
# Drawing types:
# Snake - Click to place tail, then arrow keys to extrude a snake. enter to finish
# Wall - Click to place start, then click to place end, in line with start
# Apple - Click to place
# End - click to place
# Eraser - rectangular selection

# Overlays:
# The grid (1 wide, at top left of squares)

# TODO by v1.1
# Sheer awesomeness.

# As of v1.0, profiling is useless: 108.268 s run leaves 3.852 s
# non-waiting; removing the large unavoidables gives 1.57 s
# remaining: 1.45 percent, decreasing when startup costs are ignored
#


class Editor():
    def __init__(self, levelpath):

        pygame.init()
        self.xsize = 20 * XSIZE + 60
        self.ysize = 20 * YSIZE + 40
        # TODO funky drawing idea: every blit, update a color, and draw in on
        # another screen half below, to show frequency of updates (visual debug/profile)
        # theoretically, use fadeout on all pixels (using numpy + other tricks)
        self.screen = pygame.display.set_mode((self.xsize,self.ysize), 0,32)
        pygame.display.set_caption('Snake Level Editor')

        self.colormode = "default"
        self.mode = "LEVEL"# can be "LEVEL", "LEVELSET", "LEVELSETLEVEL"
        self.L = level(self.colormode, levelpath, 7, redraw=True)# Load level BEFORE menus
        self.selectedpath = levelpath

        # Draw the starting configuration
        self.rects = []
        self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
        self.LoadButtons()

    def run(self):
        self.tool = None# All tool use variables
        self.selected = None
        self.rowcenter = None
        self.snakepos = None
        self.rectcenter = None

        self.traptext = None# The text input variable (There is only one text input box
        #in the entire program: it is to be multipurpose - name, then level)
        self.shift = False
        self.control = False


        smileyclock = pygame.time.Clock()
        while True:
            # at the start of the loop
            smileyclock.tick(120)

            for event in pygame.event.get():#Event Handling
                if event.type == QUIT:
                    return self.Quit()
                elif event.type == KEYDOWN:#Keyboard
                    if (event.key == K_q and self.traptext == None) or event.key == K_ESCAPE:
                        return self.Quit()

                    elif event.key in (K_LSHIFT, K_RSHIFT):# So all shifts and controls are noted
                        self.shift = True
                    elif event.key in (K_LCTRL, K_RCTRL):
                        self.control = True

                    elif event.key == K_RETURN and self.traptext == None and self.tool != "snake" and self.mode == "LEVELSETLEVEL":
                        # this creates an image
                        self.Save()
                        self.mode = "LEVELSET"
                        self.lsetscreen.refresh()
                        self.Draw(self.lsetscreen)
                        self.DrawSet(self.panel.images())
                        m = open(self.selectedpath, "r").read().split("\n")
                        self.rects +=  self.panel.remoteSet([1],m[0])[1]
                        self.rects +=  self.panel.remoteSet([2],m[1])[1]
                        if self.toolpanel.state():
                            self.DrawSet(self.toolpanel.disable())

                    elif self.tool == "snake":
                        if event.key == K_SPACE:
                            d, u = self.panel.remoteEnable(0)
                            self.DrawSet(d)
                            self.rects += u
                            self.snakepos = None
                            self.toolpanel.select(0)
                            self.DrawSet(self.toolpanel.enable())
                            print("Completed snake.")

                        if event.key in (K_UP,K_DOWN,K_RIGHT,K_LEFT) and self.snakepos != None  and not self.panel.isAnythingOpen():
                            if event.key == K_UP:
                                pot = (self.snakepos[0],(self.snakepos[1]-1)%YSIZE)
                            elif event.key == K_RIGHT:
                                pot = ((self.snakepos[0]+1)%XSIZE,self.snakepos[1])
                            elif event.key == K_DOWN:
                                pot = (self.snakepos[0],(self.snakepos[1]+1)%YSIZE)
                            elif event.key == K_LEFT:
                                pot = ((self.snakepos[0]-1)%XSIZE,self.snakepos[1])

                            if self.L.square(pot) not in ('X','S'):
                                self.snakepos = pot
                                print("Extending snake to " + str(self.snakepos)+ ".")
                                self.DrawSet(self.L.setSnake(self.snakepos))

                    elif self.traptext == None and self.tool != "snake" and not self.panel.isAnythingOpen() and self.mode != "LEVELSET":
                        if event.key == K_SPACE or event.key == K_n:
                            self.tool = None
                            self.DrawSet(self.toolpanel.select(0))
                        elif event.key == K_e:
                            self.tool = "end"
                            self.DrawSet(self.toolpanel.select(1))
                        elif event.key == K_w:
                            self.tool = "wall"
                            self.DrawSet(self.toolpanel.select(2))
                        elif event.key == K_a:
                            self.tool = "apple"
                            self.DrawSet(self.toolpanel.select(3))
                        # Conspicuously absent .select(4): the snake that disables all anyway
                        elif event.key == K_x:
                            self.tool = "eraser"
                            self.DrawSet(self.toolpanel.select(5))
                        elif event.key == K_s and self.control == False:
                            self.tool = "snake"
                            self.DrawSet(self.toolpanel.disable())
                            d, u = self.panel.remoteDisable(0)
                            self.DrawSet(d)
                            self.rects += u

                    elif self.tool != "snake" and  self.traptext != None:
                        if event.key == K_BACKSPACE and self.control == True:
                            self.rects += self.panel.remoteWrite(False)[1]
                        elif event.key == K_BACKSPACE:
                            self.rects += self.panel.remoteWrite(None)[1]
                        elif event.key == K_RETURN:
                            self.traptext = None
                            self.WriteTextbox(self.panel.getOpen())
                            if self.mode != "LEVELSET":
                                self.DrawSet(self.toolpanel.enable())
                            self.rects += self.panel.closeAll()[1]
                        else:
                            try:
                                letter = LETTERDICT[(event.key,self.shift)]
                                self.rects += self.panel.remoteWrite(letter)[1]
                            except KeyError:
                                pass

                elif event.type == KEYUP:
                    if event.key in (K_LSHIFT, K_RSHIFT):
                        self.shift = False
                    elif event.key in (K_LCTRL, K_RCTRL):
                        self.control = False

                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    command = self.click(True, pos)

                    if command == "FIELD" and self.snakepos == None:
                        self.highlightSquare(pos)

                elif event.type == MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    command = self.click(False, pos)

                    if command in ("TITLE","AUTHOR"):
                        # end snakiness: it is the easiest way, by far
                        if self.tool == "snake":
                            d, u = self.panel.remoteEnable(0)
                            self.DrawSet(d)
                            self.rects += u
                            self.snakepos = None
                            self.tool = None
                            self.toolpanel.select(0)
                            self.DrawSet(self.toolpanel.enable())
                            print("Completed snake.")
                    
                    if command not in ("TITLE","AUTHOR",None) and self.traptext != None:
                        self.traptext = None

                    if command == None:
                        if self.selected != None:
                            self.unhighlightSquare()
                    elif command == "A":
                        self.tool = "apple"
                    elif command == "W":
                        self.tool = "wall"
                    elif command == "E":
                        self.tool = "end"
                    elif command == "S":
                        self.tool = "snake"
                        self.DrawSet(self.toolpanel.disable())
                        d, u = self.panel.remoteDisable(0)
                        self.DrawSet(d)
                        self.rects += u
                    elif command == "X":
                        self.tool = "eraser"
                    elif command == "N":
                        self.tool = None
                    elif command == "QUIT":
                        return self.Quit()
                    elif command == "SAVE":
                        self.Save()

                    elif command == "FIELD" and self.snakepos == None:
                        self.alterField(pos)

                    elif command in ("TITLE","AUTHOR"):
                        if self.traptext != command:
                            self.WriteTextbox(self.traptext)
                            self.traptext = command
                        else:
                            if self.mode != "LEVELSET":
                                self.DrawSet(self.toolpanel.enable())
                            self.traptext = None

                    elif command in ("DEFAULT","INVERTED", "GRAY","WORM"):
                        self.colormode = command.lower()
                        self.L.setColors(self.colormode)
                        if self.mode != "LEVELSET":
                            self.RedrawLevel((0,0,XSIZE*20,YSIZE*20))
                            self.DrawSet(self.panel.images())

                    elif command[:5] == "NAME.":
                        # the selector jumps us out of the individual level as well... or make it give us the sub-level?
                        self.selectedpath = command[5:]

                    elif command == "OPEN":
                        if self.mode == "LEVEL":
                            self.Save()
                            self.L = level(self.colormode, self.selectedpath, 7, redraw=True)# Load level BEFORE menus
                            self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
                            self.DrawSet(self.toolpanel.enable())
                            self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
                            self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]
                            self.rects += self.panel.closeAll()[1]
                        else:
                            self.Save()# must be before loadLevelSet, mode change
                            if self.mode == "LEVELSETLEVEL":
                                self.mode = "LEVELSET"
                            self.lsetscreen.setSource(self.loadLevelSet())
                            self.Draw(self.lsetscreen)
                            self.DrawSet(self.panel.images())

                    elif command == "LS.<<":
                        self.DrawSet(self.lsetscreen.dec())
                    elif command == "LS.>>":
                        self.DrawSet(self.lsetscreen.inc())

                    elif command[:4] == "ADD ":
                        # implicitly, self.mode == "LEVELSET"
                        self.Save()
                        newpath = LevelSetInsert(self.lsetscreen.getpath(), (command=="ADD AFTER"))
                        self.mode = "LEVELSETLEVEL"
                        self.L = level(self.colormode, newpath, 7, redraw=True)
                        self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
                        self.DrawSet(self.toolpanel.enable())
                        self.levelsetsize += 1
                        self.mode = "LEVELSET"
                        self.Save()
                        self.mode = "LEVELSETLEVEL"

                        self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
                        self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]
                        pass
                        
                    elif command == "EDIT":
                        # implicitly, self.mode == "LEVELSET"
                        self.mode = "LEVELSETLEVEL"
                        self.L = level(self.colormode, self.lsetscreen.getpath(), 7, redraw=True)
                        self.RedrawLevel((0,0,XSIZE*20,YSIZE*20))
                        self.rects += self.panel.closeAll()[1]
                        self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
                        self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]
                        self.DrawSet(self.toolpanel.enable())

                    elif command == "NEW":# create a new level/levelset
                        self.Save()
                        if self.mode == "LEVEL":
                            self.L = level(self.colormode, NewAddress(0, True), 7, redraw=True)
                            self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
                            self.DrawSet(self.toolpanel.enable())
                            self.rects += self.panel.closeAll()[1]
                            self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
                            self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]
                        elif self.mode == "LEVELSET":
                            # create a new levelset, with one empty level in it
                            self.Save()
                            self.selectedpath = self.createNewLevelSet()
                            self.loadLevelSet()
                            self.Draw(self.lsetscreen)
                        elif self.mode == "LEVELSETLEVEL":
                            # append a level to this levelset and work on it
                            self.Save()

                            self.L = level(self.colormode, NextOpenLPath(self.levelsetpath[:-8]), 7, redraw=True)
                            self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
                            self.DrawSet(self.toolpanel.enable())
                            self.levelsetsize += 1
                            self.mode = "LEVELSET"
                            self.Save()
                            self.mode = "LEVELSETLEVEL"

                            self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
                            self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]
                            pass

                        self.rects += self.panel.closeAll()[1]

                    elif command == "INDIVIDUAL":
                        self.Save()
                        self.mode = "LEVEL"
                        self.RedrawLevel((0,0,XSIZE*20, YSIZE*20))
                        self.selectedpath = self.panel.remoteRead([0,1,1])
                        self.panel.remoteSet([0,1,1], LevelSource(0, True))
                        self.DrawSet(self.panel.images())

                    elif command == "LEVELSET":
                        # open the default levelset entry point
                        # we let this pass: it affects a nonopen submenu
                        self.Save()
                        self.panel.remoteSet([0,1,1], LevelSource(0, False))
                        self.mode = "LEVELSET"  # must be after Save
                        self.selectedpath = "levels/levelset/000/Info.txt"
                        self.lsetscreen.setSource(self.loadLevelSet())
                        self.lsetscreen.disable()
                        self.Draw(self.lsetscreen)
                        self.DrawSet(self.panel.images())

            if self.rowcenter != None:
                self.rowHighlight(pygame.mouse.get_pos())
            elif self.rectcenter != None:
                self.rectHighlight(pygame.mouse.get_pos())

            # At the end of the loop
            if len(self.rects) > 0:
                pygame.display.update(self.rects)

                self.rects = []
# ------------------------------------------ FIELD ALTERATION -----------------------------------------------------------------------------

    def alterField(self, pos):
        spos = (pos[0]//20, pos[1]//20)# the square in question

        if self.tool == None:
            return

        if self.tool == "wall":
            self.rowcenter = None

            sx,sy = self.selected[0]//20,self.selected[1]//20
            if self.selected[2] == 20 and self.selected[3] == 20:
                if spos == (sx,sy):
                    if self.L.square(spos) not in ("X","S","H"):
                        self.L.setSquare("H", spos)
                        self.RedrawLevel(expand(self.selected, 2))
                return
            elif self.selected[2] == 20:
                dy = self.selected[3]//20
                for i in range(0, dy):
                    if self.L.square((sx,sy+i)) not in ("X","S","H"):
                        self.L.setSquare("H", (sx,sy+i))
                self.RedrawLevel(expand(self.selected, 2))
            elif self.selected[3] == 20:# an else would never be called
                dx = self.selected[2]//20

                for i in range(0, dx):
                    if self.L.square((sx+i,sy)) not in ("X","S","H"):
                        self.L.setSquare("H", (sx+i,sy))

                self.RedrawLevel(expand(self.selected, 2))
        if self.tool == "end":
            if self.L.square(spos) not in ("X","S"):
                print("Creating an end at "+ str(spos) + ".")
                self.L.setSquare("E", spos)
            self.RedrawLevel(expand(self.selected, 2))
            return

        if self.tool == "eraser":
            self.rectcenter = None

            sx, sy = self.selected[0]//20, self.selected[1]//20
            for dx in range(self.selected[2]//20):
                for dy in range(self.selected[3]//20):
                    if self.L.square((sx+dx,sy+dy)) not in ("X","S","."):
                        self.L.setSquare(".", (sx+dx,sy+dy))
                        print("Erasing at "+ str((sx+dx,sy+dy)) + ".")
            self.RedrawLevel(expand(self.selected, 2))
            return

        if self.tool == "apple":
            if self.L.square(spos) not in ("X","S"):
                self.L.setSquare("A", spos)
                print("Creating an apple at "+ str(spos) + ".")
            self.RedrawLevel(expand(self.selected, 2))
            return

        if self.tool == "snake":
            if self.snakepos == None and spos[0] == self.selected[0]//20 and spos[1] == self.selected[1]//20:
                self.snakepos = spos
                print("Creating a snake at " + str(self.snakepos)+ ".")
                self.DrawSet(self.L.clearOldSnake(self.snakepos))

# ------------------------------------------ FIELD ALTERATION -----------------------------------------------------------------------------
# ------------------------------------------ CLICK HANDLING -------------------------------------------------------------------------------

    def LoadButtons(self):
        # SIDE PANEL

        self.toolpanel = Sidebar([
            # crazy idea: update these colors to match
            # their colorscheme equivalents; use highlighting
            # for graytones
            toolbutton("N", (0,0,0), (100,100,100)),# Nothing
            toolbutton("E", (0,0,0), (100,100,100)),# End
            toolbutton("W", (0,0,0), (100,100,100)),# Wall
            toolbutton("A", (0,0,0), (100,100,100)),# Apple
            toolbutton("S", (0,0,0), (100,100,100)),# Snake
            toolbutton("X", (0,0,0), (100,100,100)),# Erase
            ])
        self.toolpanel.setpos((XSIZE*20, 0))

        self.toolpanel.select(0)# None

        self.Draw(self.toolpanel)

        # MAIN PANEL

        self.panel = SuperPanel(self.screen,
            [
                [button("OPTIONS", C.new, LOCK_BUTTON),
                SuperMenu([
                    [button("MODE",C.options, LOCK_BUTTON),
                    SelectorMenu([
                        button("INDIVIDUAL", C.individual, ITEM_BUTTON),
                        button("LEVELSET", C.levelset, ITEM_BUTTON)],
                    C)],
                    [button("LEVEL", C.options, LOCK_BUTTON),
                    SuperMenu(
                        [
                            [button("NEW", C.new, PLAIN_BUTTON)],
                            [button("SELECT", C.new, LOCK_BUTTON),
                            ListMenu("SELECT", 400, C.new, C, LevelSource(0, True) )],
                            [button("OPEN", C.new, PLAIN_BUTTON)]
                        ],

                    C)],
                    [button("THEME", C.options, LOCK_BUTTON),
                    SelectorMenu([
                        button("DEFAULT", C.default, ITEM_BUTTON),
                        button("INVERTED", C.inverted, ITEM_BUTTON),
                        button("GRAY", C.graybutton, ITEM_BUTTON),
                        button("WORM", C.worm, ITEM_BUTTON)],
                    C)]
                    ], C)
                ]
            ],[
                [inputbox(200, C.levelselect, C.button, "TITLE")],
                [inputbox(200, C.levelselect, C.button, "AUTHOR")]
            ],[
                [button("SAVE", C.save, PLAIN_BUTTON)],
                [button("QUIT", C.quit, PLAIN_BUTTON)]
            ])

        self.rects += self.panel.remoteSet([1],self.L.F.getname())[1]
        self.rects += self.panel.remoteSet([2],self.L.F.getauthor())[1]

        # set leveleditor mode (level v levelset)
        self.rects += self.panel.remoteSet([0,0],{"LEVEL":0,"LEVELSET":1,"LEVELSETLEVEL":1}[self.mode])[1]

        # set colormode
        self.rects += self.panel.remoteSet([0,2],0)[1]
        self.rects.append(self.panel.getrect())

        self.lsetscreen = LevelSetScreen(
        [
            button("ADD BEFORE", C.default, PLAIN_BUTTON),
            button("EDIT", C.pause, PLAIN_BUTTON),
            button("ADD AFTER", C.default, PLAIN_BUTTON)
        ],[
            tributton("LS.<<", 50, 100, False),
            tributton("LS.>>", 50, 100, True)
        ],
        emptyfeed()
        )

    def click(self, state, pos):
        if not state:
            self.unhighlightSquare()

        # ugh. There is a way to control ownership: rewrite the menu code to add a clickhit, or just go wheee! and add a huge array
        wasopen = self.panel.isAnythingOpen()

        dp, up, cp = self.panel.click(state, pos)
        ct = None
        self.UndrawSet(up)# Order matters
        self.DrawSet(dp)
        # better yet, how to distinguish a miss from a nothing.

        # enable/disable
        if wasopen and not self.panel.isAnythingOpen() and self.tool != 'snake':
            if not self.mode == "LEVELSET":
                self.DrawSet(self.toolpanel.enable())
            elif self.mode == "LEVELSET":
                self.DrawSet(self.lsetscreen.enable())
        elif not wasopen and self.panel.isAnythingOpen() and self.tool != 'snake':
            self.DrawSet(self.toolpanel.disable())
            if self.mode == "LEVELSET":
                self.DrawSet(self.lsetscreen.disable())


        # main window interaction
        if not self.panel.isAnythingOpen():
            if self.mode == "LEVELSET":
                dt, ut, ct = self.lsetscreen.click(state, pos)
                self.DrawSet(dt)
            else:
                dt, ut, ct = self.toolpanel.click(state, pos)
                self.DrawSet(dt)
                if pos[0] < XSIZE * 20 and pos[1] < YSIZE*20:
                    return "FIELD"

        if state == True:
            return None
        else:
            if cp == None:
                return ct# which may also be none
            else:
                return cp

    def rowHighlight(self, pos):

        # erase the old
        x,y= self.rowcenter
        if pos[0] > XSIZE*20:
            pos = (XSIZE*20,pos[1])
        if pos[1] > YSIZE*20:
            pos = (pos[0],YSIZE*20)
        px, py = pos[0]//20, pos[1]//20

        if x == px:
            if pos[1]/20 < y:
                k = (x, Floor(pos[1]/20), 1, y - Floor(pos[1]/20) + 1)
            else:
                k = (x, y, 1, Ceiling(pos[1]/20) - y)
        elif y == py:
            if pos[0]/20 < x:
                k = (Floor(pos[0]/20), y, x - Floor(pos[0]/20) + 1, 1)
            else:
                k = (x, y, Ceiling(pos[0]/20) - x, 1)
        else:
            k = (x, y, 1, 1)

        k = [(i * 20) for i in k]# blocks -> pixels

        if self.selected != k:
            self.RedrawLevel(self.selected)
            self.selected = k
            self.drawHighlight()
        return

    def rectHighlight(self, pos):
        x,y = self.rectcenter# expand
        if pos[0] > XSIZE*20:# limit pos to the field
            pos = (XSIZE*20,pos[1])
        if pos[1] > YSIZE*20:
            pos = (pos[0],YSIZE*20)

        # 2 cases for x and for y
        k = [0,0,0,0]
        if pos[0]/20 <= x:# LEFT
            k[0] = (Floor(pos[0]/20))        *20
            k[2] = (x - Floor(pos[0]/20) + 1)*20
        else:           # RIGHT
            k[0] = (x)                       *20
            k[2] = (Ceiling(pos[0]/20) - x)  *20

        if pos[1]/20 <= y:#UP
            k[1] = (Floor(pos[1]/20))        *20
            k[3] = (y - Floor(pos[1]/20) + 1)*20
        else:          # DOWN
            k[1] = (y)                       *20
            k[3] = (Ceiling(pos[1]/20) - y)  *20

        if self.selected != k:
            self.RedrawLevel(self.selected)
            self.selected = k
            self.drawHighlight()
        return

    def drawHighlight(self):
        # draw the new
        overlay = pygame.Surface((self.selected[2],self.selected[3]))
        overlay.fill((127,127,127))
        overlay.set_alpha(127)
        self.screen.blit(overlay, (self.selected[0],self.selected[1]))
        self.rects.append(self.selected)

    def highlightSquare(self, pos):
        if self.tool == "wall":
            self.rowcenter = (pos[0]//20, pos[1]//20)
        if self.tool == "eraser":
            self.rectcenter = (pos[0]//20, pos[1]//20)

        self.selected = (pos[0]//20*20, pos[1]//20*20, 20, 20)
        self.drawHighlight()

    def unhighlightSquare(self):
        if self.selected != None and self.mode != "LEVELSET":
            self.RedrawLevel(self.selected)
        self.rowcenter = None
        self.rectcenter = None

# ------------------------------------------ CLICK HANDLING -------------------------------------------------------------------------------
# ------------------------------------------- BASIC FUNCTIONS -----------------------------------------------------------------------------

    # returns the subiterator of levels
    # for the levelset marked by self.selectedpath
    def loadLevelSet(self):
        print("opened", self.selectedpath)
        m = open(self.selectedpath, "r").read().split("\n")
        # set name/author
        self.rects +=  self.panel.remoteSet([1],m[0])[1]
        self.rects +=  self.panel.remoteSet([2],m[1])[1]
        self.levelsetsize = int(m[2])
        self.levelsetpath = self.selectedpath
        # we really do not care about the last number (# of levels);-)

        return LSLevelSource(self.selectedpath[-12:-9], 0)

    def createNewLevelSet(self):
        """ Create a new levelset, containing
            one default level"""
        # iterate up folders; create one;
        # write a default Info.txt
        # set self.L to be the level 000.txt inside
        path = NextLSet()
        self.L = level(self.colormode, path[:-8]+"000.txt", 7, redraw=True)
        self.L.F.write()

        return path

    def Quit(self):
        # expert trick ;-) (if level botched up)
        if not self.control and not self.shift:
            self.Save()
        return "Oog was here. :-)"

    def Save(self):
        if self.mode == "LEVELSET":
            open(self.levelsetpath, "w").write(self.panel.remoteRead([1])+"\n"+self.panel.remoteRead([2])+"\n"+str(self.levelsetsize))
        else:
            self.L.F.write()
            self.L.saveImg()
        print("Saving...")

    def RedrawLevel(self, rect):
        self.DrawSet(self.L.getSections([rect]))

    def Draw(self,item):# a simple function. pass a button, menu, counter and behold! it draws it
        self.screen.blit(item.image(), item.getpos())
        self.rects.append(item.getrect())

    def UndrawSet(self, udraw):# takes an array of rects, sent from menu system
        if self.mode == "LEVELSET":
            for rect in udraw:
                self.DrawSet(self.lsetscreen.getSections([rect]));
        else:
            for rect in udraw:
                self.RedrawLevel(rect)

    def DrawSet(self, draw):# takes an array of (image, pos) pairs, sent from the menu system
        for img in draw:
            self.screen.blit(img[0], img[1])
            self.rects.append((img[1][0], img[1][1], img[0].get_size()[0], img[0].get_size()[1]))

    def WriteTextbox(self, command):
        if command == "TITLE":
            self.L.F.setname(self.panel.remoteRead([1]))
        else:
            self.L.F.setauthor(self.panel.remoteRead([2]))

# ------------------------------------------- BASIC FUNCTIONS -----------------------------------------------------------------------------

def expand(rect, width):# expands a selection rect by width in each direction
    return (rect[0]-width, rect[1]-width, rect[2]+2*width, rect[3]+2*width)

def stacktrace():
    try:
        pprint.pprint(inspect.stack())
    except:
        import inspect, pprint
        pprint.pprint(inspect.stack())

if __name__ == "__main__":
    import sys
    if "-d" in sys.argv:
        import cProfile
        cProfile.run("print(Editor(\"levels/individual/000.txt\").run())", "profile.txt")
        import pstats
        p = pstats.Stats("profile.txt")
        p.sort_stats('time').print_stats(50)
    else:
        print(Editor("levels/individual/000.txt").run())

    quit()