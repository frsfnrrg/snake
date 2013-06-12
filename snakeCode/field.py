# -*- coding: utf-8 -*-
from snakeCode.constants import *
from snakeCode.snake import snake
import os
from snakeCode.colors import COLORLIST

# WARNING File Deletion and writing occurs in write. Do not mess it up. WARNING

class field():
    def __init__(self, address):
        self.path = address
        try:
            f = open(self.path,"r").read().split("\n")

            self.grid = []# Note that self.grid is accessed in g[x][y]
            self.apples = 0
            for z in range(XSIZE):
                self.grid.append([])
                for w in range(YSIZE):
                    self.grid[z].append(f[w][z])
                    if self.grid[z][w] == "A":
                        self.apples += 1

            self.S = snake(f[YSIZE])# Initialize Snake. The line after
            #Note: Snake is still accessible. ex. Field.S.addDirection()

            try:
                self.title = f[YSIZE+1]
            except IndexError:
                self.title = "Unknown"
            try:
                self.creator = f[YSIZE+2]
            except IndexError:
                self.creator = "Unknown"
            self.changed = False

        except IOError:
            self.grid = [["."]*YSIZE for i in range(XSIZE)]
            self.apples = 0
            self.S = snake("0 0 1 0")# Invisible snake, to be created
            self.grid[0][0] = "X"
            self.grid[1][0] = "S"
            self.title = "Unknown"
            self.creator = "Unknown"
            self.changed = True

    def __getitem__(self,pos):# this allows easy access for drawing, etc. Field[x][y]
        # maybe make it Field[(x,y)] for cleanliness and better access
        return self.grid[pos]

    # Extra details of the level
    def getname(self):
        return self.title

    def setname(self, name):
        if name != self.title:
            self.title = name
            self.changed = True

    def getauthor(self):
        return self.creator

    def setauthor(self, name):
        if name != self.creator:
            self.creator = name
            self.changed = True


    def update(self):
        self.S.updatePosition()

        # variable used for legibility; this is where the Snake's head rams into things
        z = self.grid[self.S[0][0]][self.S[0][1]]

        if z == "H":
            return "WALL"# Wall collision

        if z == "S" and self.S[0] != self.S.getOldEnd():
            return "SELF"

        if z == "A":
            self.apples -= 1# Ate an apple
            self.S.getFatter()

        if z == "E":
            if self.apples == 0:
                self.S.setWinMode(True)
                return "WIN"# Win
            else:
                return "EXIT"# Leave too early

        self.grid[self.S[0][0]][self.S[0][1]] = "X"# place head
        self.grid[self.S[1][0]][self.S[1][1]] = "S"# replace old head with a neck
        if self.S.getOldEnd() != None:# if snake is not growing
            self.grid[self.S.getOldEnd()[0]][self.S.getOldEnd()[1]] = "."# clear old tail

        return None

    def win(self):
        end = self.S.winAnim()
        if end == None:
            return False
        else:
            self.grid[end[0]][end[1]] = "."


    # LEVEL EDITOR CHANGE FUNCTIONS

    def set(self, value, pos):
        self.grid[pos[0]][pos[1]] = value
        if value == "A":
            self.apples += 1
        self.changed = True

    def write(self):
        if self.changed == False:
            return
        text = ""
        for y in range(YSIZE):
            for x in range(XSIZE):
                text += self.grid[x][y]
            text += "\n"

        for s in self.S:
            text += str(s[0]) + " " + str(s[1]) + " "
        text += "\n"

        text += self.title + "\n"
        text += self.creator

        open(self.path,"w").write(text)
        self.changed = False

        # Delete the images of the file
        for theme in COLORLIST:
            k = self.path[:-4] + "_" + theme + ".png"
            if os.path.exists(k):
                print("Deleting old image at \'" + k + "\'.")
                os.remove(k)
