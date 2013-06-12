# -*- coding: utf-8 -*-
import pygame, os

from snakeCode.colors import LevelColors
from snakeCode.field import field# & snake with it
from snakeCode.constants import *


# Level is to be recreated every time a new level is loaded
# Xpos, ypos are assumed to be simply (0,0)
# level.F,S is free to outside access
# self.F,self.I, self.C; field, image, colors

class level():
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////// Externally called ////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    def __init__(self, colorscheme, leveladdress, speed, redraw=False):#ex. "inverted", "levels/individual/000", 20
        self.redraw = redraw
        # speed dealt with
        self.setSpeed(speed)

        self.leveladdress = leveladdress
        self.F = field(leveladdress)

        self.tick = self.tickmodulo - 1# so it starts immediately
        self.move = 0# will be move1 on start
        self.state = None# what mode it is in.
        self.winstate = 0# 0 - not, 1-snake dissappears, 2-done
        self.rects = []

        self.C = LevelColors()

        self.C.setColorScheme(colorscheme)

        self._drawField()

    def setColors(self, colorscheme):
        self.C.setColorScheme(colorscheme)

        self._drawField()

        return self.getSections([(0,0,XSIZE*20, YSIZE*20)])

# -------------------------- GAME ACCESS---------------------------------------------------------------------------------------------------

    def incSpeed(self):
        return self.setSpeed({7:10,10:14,14:20,20:20}[self.speed])

    def decSpeed(self):
        return self.setSpeed({20:14,14:10,10:7,7:7}[self.speed])

    def setSpeed(self, speed):
        self.speed = speed
        self.fps = {20:60,14:56,10:60,7:56}[self.speed]
        self.tickmodulo = {20:3,14:4,10:6,7:8}[self.speed]
        return self.speed

    def getSpeed(self):
        return self.speed

    def isWinning(self):
        if self.winstate not in (0,3):
            return False
        return True

    def update(self):
        if self.state != None and self.state != "WIN":# if you crash, it stops
            return [], self.state, False

        self.tick += 1
        if self.tick >= self.tickmodulo and self.winstate != 3:
            self.tick %= self.tickmodulo
            self.move += 1
        elif self.winstate == 3:
            return [], "WIN", False
        else:
            return [], None,  False# Nothing to draw, status none

        self.rects = []

        # FIELD/SNAKE updates
        if self.winstate == 0:
            self.state = self.F.update()
            if self.state == None:
                self._addRects(self._redrawSnake())#
            elif self.state == "WIN":
                self.winstate = 1
                self.F.S.setWinMode(False)
        elif self.winstate == 1:# winanim starts
                self._addRects(self._redrawSnake())
                self._addRects(self._drawWinSnake())
                self.winstate = 2

        # this if advances winanim in the process
        elif self.winstate == 2 and self.F.win() == False:#if there is no more snake to be consumed; update, proceed
            self._addRects(self._drawFinSnake())
            self.winstate = 3# this gives a 1 turn pause before reloading
        elif self.winstate == 2:# if it is still in end mode, redraw/ If not, then not
            self._addRects(self._redrawWinSnake())

        if self.winstate == 0:
            return self.getSections(self.rects), None, True# the last is whether any moves have been made ingame
        else:
            return self.getSections(self.rects), None, False

    def getFPS(self):# returns the fps rate the clock is to tick at: 56, 60 fps. 140 is lcm(20,14,10,7) but c'est trop
        return self.fps

    def getSections(self, rects):# takes a list of rectangles, returns a list of image/pos pairs
        draw = []
        for rect in rects:
            if rect == (0,0,XSIZE*20, YSIZE*20):
                return [(self.I,(0,0))]

            if rect[1] + rect[3] >= YSIZE*20:# Bound to the field
                rect = (rect[0], rect[1], rect[2], YSIZE*20 - rect[1])
            if rect[0] + rect[2] >= XSIZE*20:
                rect = (rect[0], rect[1], XSIZE*20 - rect[0], rect[3])

            subimage = pygame.Surface((rect[2],rect[3]))
            subimage.blit(self.I, (0,0), rect)
            draw.append((subimage, (rect[0],rect[1])))

        return draw

# ------------------------------- EDITOR ACCESS--------------------------------------------------------------------------------------------

    def square(self, pos):
        return self.F[pos[0]][pos[1]]

    def setSquare(self, value, pos):
        self.F.set(value, pos)
        self._editorDrawSquare(pos[0], pos[1])

    def setSnake(self, spos):# spos is constrained by being adjacent to last snake block
        r = []
        self.F.S.editorAdd(spos)
        self.F.set("X", spos)

        self.snakearray[spos[0]][spos[1]] = len(self.F.S)
        self._editorDrawSquare(spos[0], spos[1])
        r.append((spos[0]*20 - 2, spos[1]*20 - 2, 24, 24))

        if len(self.F.S) > 1:# Manage old head
            self.F.set("S", self.F.S[1])

            self._editorDrawSquare(self.F.S[1][0], self.F.S[1][1])
            r.append((self.F.S[1][0]*20 - 2, self.F.S[1][1]*20 - 2, 24, 24))

            if len(self.F.S) > 2:
                r.append((self.F.S[2][0]*20 - 2, self.F.S[2][1]*20 - 2, 24, 24))

        #print(r)

        return self.getSections(r)

    def clearOldSnake(self,spos):# This function was .. enjoyable ... to order correctly
        # CLEAR
        for s in self.F.S:
            self.setSquare(".", s)
            self.snakearray[s[0]][s[1]] = 0
        r = []
        for s in self.F.S:
            self._editorDrawSquare(s[0], s[1])
            r.append((s[0]*20-2,s[1]*20-2, 24, 24))

        self.F.S.editorClear()
        # ADD NEW HEAD
        i = self.setSnake(spos)

        return self.getSections(r) + i

    def saveImg(self):
        imgpath = self.leveladdress[:-4]+"_"+self.C.getColorScheme()+".png"
        pygame.image.save(self.I, imgpath)
        
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ////////////////////////////////////////// Internally called ////////////////////////////////////////////////////////////////////////////
# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# These functions are prefixed with underscores

    def _drawField(self):# redraw the entire field
        if self.move == 0:
            self.I = pygame.Surface((XSIZE*20, YSIZE*20))
            imgpath = self.leveladdress[:-4]+"_"+self.C.getColorScheme()+".png"
            if os.path.exists(imgpath) and self.redraw == False:
                img = pygame.image.load(imgpath)
                self.I.blit(img, (0,0))
                del img
                return

        # DRAW
        self.I.fill(self.C.bg)# fill w/ background
        self._snakeArray()# create Snake array- to draw snake bits

        for xpos in range(XSIZE):# For each block in the area to be redrawn...
            for ypos in range(YSIZE):
                self._drawSquare(xpos, ypos)

        if self.move == 0:
            pygame.image.save(self.I, imgpath)
        return

    def _editorDrawSquare(self, xpos, ypos):
        pygame.draw.rect(self.I, self.C.bg, (xpos*20-2,ypos*20-2,24,24))# clear the region of impact: then add on again

        self._undoHeadCut(xpos, ypos)# if the clear cut away the snake's head, fix snake

        if self.F[xpos][ypos] == "H":# wall
            pygame.draw.rect(self.I, self.C.wall, (xpos*20+2,ypos*20+2,16,16))
            self._editorWallConnect((xpos, ypos), "H", self.C.wallconnect)

        if self.F[xpos][ypos] == "E":# exit
            pygame.draw.rect(self.I, self.C.goal, (xpos*20+2,ypos*20+2,16,16))

        if self.F[xpos][ypos] == "A":# apple
            pygame.draw.rect(self.I, self.C.banana, (xpos*20+2,ypos*20+2,16,16))

        if self.F[xpos][ypos] == "X":# Snakehead
            pygame.draw.rect(self.I, self.C.snake, (xpos*20,ypos*20,20,20))

        if self.F[xpos][ypos] == "S":# snakebody
            pygame.draw.rect(self.I, self.C.snake, (xpos*20+2,ypos*20+2,16,16))
            k = self.snakearray[xpos][ypos]
            self._drawSnakeJoints(k)
            if k != 0:
                self._drawSnakeJoints(k-1)# With step by step redrawing, we have some problems without this when creating snake
                # this is a quickfix: remove, specialize and put into _undoheadcut for S-S case for speed purposes

    def _undoHeadCut(self, xpos, ypos):
        if self.F[(xpos+1)%XSIZE][ypos] == "X": # RIGHT
            pygame.draw.rect(self.I, self.C.snake, (xpos*20+20,ypos*20,2,20))
        if self.F[(xpos-1)%XSIZE][ypos] == "X": # LEFT
            pygame.draw.rect(self.I, self.C.snake, (xpos*20-2,ypos*20,2,20))
        if self.F[xpos][(ypos+1)%YSIZE] == "X": # DOWN
            pygame.draw.rect(self.I, self.C.snake, (xpos*20,ypos*20+20,20,2))
        if self.F[xpos][(ypos-1)%YSIZE] == "X": # UP
            pygame.draw.rect(self.I, self.C.snake, (xpos*20,ypos*20-2,20,2))

            # CORNERS!
        if self.F[(xpos+1)%XSIZE][(ypos+1)%YSIZE] == "X": # RIGHT, DOWN
            pygame.draw.rect(self.I, self.C.snake, (xpos*20+20,ypos*20+20,2,2))
        if self.F[(xpos-1)%XSIZE][(ypos+1)%YSIZE] == "X": # LEFT, DOWN
            pygame.draw.rect(self.I, self.C.snake, (xpos*20-2,ypos*20+20,2,2))
        if self.F[(xpos+1)%XSIZE][(ypos-1)%YSIZE] == "X": # RIGHT, UP
            pygame.draw.rect(self.I, self.C.snake, (xpos*20+20,ypos*20-2,2,2))
        if self.F[(xpos-1)%XSIZE][(ypos-1)%YSIZE] == "X": # LEFT, UP
            pygame.draw.rect(self.I, self.C.snake, (xpos*20-2,ypos*20-2,2,2))

    def _editorWallConnect(self, pos, t, color):
        xpos, ypos = pos
        if self.F[(xpos+1)%XSIZE][ypos] == t:
            self._drawJoint((xpos,ypos),(1,0),color)
            self._drawJoint(((xpos+1)%XSIZE,ypos),(-1,0),color)
        if self.F[(xpos-1)%XSIZE][ypos] == t:
            self._drawJoint((xpos,ypos),(-1,0),color)
            self._drawJoint(((xpos-1)%XSIZE,ypos),(1,0),color)
        if self.F[xpos][(ypos+1)%YSIZE] == t:
            self._drawJoint((xpos,ypos),(0,-1),color)
            self._drawJoint((xpos,(ypos+1)%YSIZE),(0,1),color)
        if self.F[xpos][(ypos-1)%YSIZE] == t:
            self._drawJoint((xpos,ypos),(0,1),color)
            self._drawJoint((xpos,(ypos-1)%YSIZE),(0,-1),color)

    def _drawSquare(self, xpos, ypos):
        if self.F[xpos][ypos] == "H":# wall

            pygame.draw.rect(self.I, self.C.wall, (xpos*20+2,ypos*20+2,16,16))
            if self.F[(xpos+1)%XSIZE][ypos] == "H":
                self._drawJoint((xpos,ypos),(1,0),self.C.wallconnect)
            if self.F[(xpos-1)%XSIZE][ypos] == "H":
                self._drawJoint((xpos,ypos),(-1,0),self.C.wallconnect)
            if self.F[xpos][(ypos+1)%YSIZE] == "H":
                self._drawJoint((xpos,ypos),(0,-1),self.C.wallconnect)
            if self.F[xpos][(ypos-1)%YSIZE] == "H":
                self._drawJoint((xpos,ypos),(0,1),self.C.wallconnect)

        if self.F[xpos][ypos] == "E":# exit
            pygame.draw.rect(self.I, self.C.goal, (xpos*20+2,ypos*20+2,16,16))
        if self.F[xpos][ypos] == "A":# apple
            pygame.draw.rect(self.I, self.C.banana, (xpos*20+2,ypos*20+2,16,16))

        if self.F[xpos][ypos] == "X":# Snakehead
            pygame.draw.rect(self.I, self.C.snake, (xpos*20,ypos*20,20,20))
        if self.F[xpos][ypos] == "S":# snakebody
            spos = self.snakearray[xpos][ypos]
            self._drawSnakeJoints(spos)
            pygame.draw.rect(self.I, self.C.snake,
                (self.F.S[spos][0]*20+2,self.F.S[spos][1]*20+2,16,16))

    def _snakeArray(self): # s[x][y] = n
        # organizational scheme: the TAIL is 1, the head is LEN(SNAKE)
        self.snakearray = []
        for x in range(XSIZE):# make a blank
            self.snakearray.append([])
            for y in range(YSIZE):
                self.snakearray[x].append(0)
        for s in range(1, len(self.F.S)+1):
            self.snakearray[self.F.S[-s][0]][self.F.S[-s][1]] = s

    def _drawJoint(self,pos,direction,color):
        #     N          W         S        E
        f = {-2:(-10,-6),-1:(-6,8),2:(8,-6),1:(-6,-10)}
        (xd,yd) = f[2*direction[0]+direction[1]]
        x,y = abs(12*direction[1]+2*direction[0]),abs(2*direction[1]+12*direction[0])# 2,12, or 12,2 depending on direction
        xpos,ypos = 20*pos[0]+10,20*pos[1]+10

        pygame.draw.rect(self.I, color, (xpos+xd,ypos+yd,x,y))

    def _redrawSnake(self):
        old = self.F.S.getOldEnd()
        if old != None:
            pygame.draw.rect(self.I, self.C.bg, (old[0]*20-2,old[1]*20-2,24,24))
            rect = [(old[0]*20-2,old[1]*20-2,24,24)]
        else:
            rect = []

        pygame.draw.rect(self.I, self.C.bg, (self.F.S[1][0]*20,self.F.S[1][1]*20,20,20))
        pygame.draw.rect(self.I, self.C.snake, (self.F.S[1][0]*20+2,self.F.S[1][1]*20+2,16,16))

        pygame.draw.rect(self.I, self.C.snake, (self.F.S[0][0]*20,self.F.S[0][1]*20,20,20))

        self._drawSnakeJoints(len(self.F.S)-1)

        rect.append((self.F.S[1][0]*20,self.F.S[1][1]*20,20,20))
        rect.append((self.F.S[0][0]*20,self.F.S[0][1]*20,20,20))

        return rect

    def _drawWinSnake(self):
        pygame.draw.rect(self.I, self.C.bg, (self.F.S[0][0]*20,self.F.S[0][1]*20,20,20))
        pygame.draw.rect(self.I, self.C.snake, (self.F.S[0][0]*20+2,self.F.S[0][1]*20+2,16,16))
        self._drawSnakeJoints(0)
        return [(self.F.S[0][0]*20,self.F.S[0][1]*20,20,20)]

    def _redrawWinSnake(self):
        old = self.F.S.getOldEnd()
        if old != None:
            pygame.draw.rect(self.I, self.C.bg, (old[0]*20-2,old[1]*20-2,24,24))
            return [(old[0]*20-2,old[1]*20-2,24,24)]
        return []

    def _drawFinSnake(self):# redraws the goal after the snake passes through.
        pygame.draw.rect(self.I, self.C.goal, (self.F.S[0][0]*20+2,self.F.S[0][1]*20+2,16,16))
        return [(self.F.S[0][0]*20+2,self.F.S[0][1]*20+2,16,16)]

    def _drawSnakeJoints(self,h):# draws the joints of the snake at a position
        # 0,1# Down
        # 0,-1# Up
        # 1,0# Right
        # -1,0# Left
        h = len(self.F.S) - h

        # Toward the head
        if 1 <= h < len(self.F.S):
            if (self.F.S[h][0] + 1)%XSIZE == self.F.S[h-1][0]:
                self._drawJoint(self.F.S[h],(1,0),self.C.snakejoint)
            elif (self.F.S[h][0] - 1)%XSIZE == self.F.S[h-1][0]:
                self._drawJoint(self.F.S[h],(-1,0),self.C.snakejoint)
            elif (self.F.S[h][1] + 1)%YSIZE == self.F.S[h-1][1]:
                self._drawJoint(self.F.S[h],(0,-1),self.C.snakejoint)
            elif (self.F.S[h][1] - 1)%YSIZE == self.F.S[h-1][1]:
                self._drawJoint(self.F.S[h],(0,1),self.C.snakejoint)

        # Toward the tail
        if 0 <= h < len(self.F.S) - 1:
            if (self.F.S[h][0] + 1)%XSIZE == self.F.S[h+1][0]:
                self._drawJoint(self.F.S[h],(1,0),self.C.snakejoint)
            elif (self.F.S[h][0] - 1)%XSIZE == self.F.S[h+1][0]:
                self._drawJoint(self.F.S[h],(-1,0),self.C.snakejoint)
            elif (self.F.S[h][1] + 1)%YSIZE == self.F.S[h+1][1]:
                self._drawJoint(self.F.S[h],(0,-1),self.C.snakejoint)
            elif (self.F.S[h][1] - 1)%YSIZE == self.F.S[h+1][1]:
                self._drawJoint(self.F.S[h],(0,1),self.C.snakejoint)

    def _addRects(self, r):
        for g in r:
            self.rects.append(g)

            