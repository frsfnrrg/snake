# -*- coding: utf-8 -*-
from snakeCode.constants import *

class snake():
    # Init
    def __init__(self,line):

        self.positions = []
        s = line.split(" ")
        for x in range(int(len(s)/2)):
            self.positions.append((int(s[2*x]),int(s[2*x+1])))
        if len(self.positions) > 1:
            self.directions = [(self.positions[0][0] - self.positions[1][0], self.positions[0][1] - self.positions[1][1])]
        else:
            self.directions = [(0,-1)]# up
        self.oldend = None
        self.extra = 0
        self.won = False# REMOVE

    # operators
    def __len__(self):
        return len(self.positions)

    def __getitem__(self,pos):# so Snake[n] returns the position of the nth snake segment
        return self.positions[pos]

    def __str__(self):# to debug if needed.
        return "Snake at "+ str(self.positions)

    # Get Info
    def getOldEnd(self):
        return self.oldend

    def getFatness(self):# Sniff... currently unused afaIk
        if self.extra == 0:
            return False
        return True

    # Directions
    def startDirection(self,d):
        # Note that direction has len 1
        # backwards
        if self.directions[0] == (-d[0],-d[1]):
            return False
        # forwards
        if self.directions[0] == d:
            return True
        # to a side
        self.directions = [d]
        return True

    def addDirection(self, d):
        if self.directions[-1] not in ((d[0],d[1]),(-d[0],-d[1])):
            self.directions.insert(0,d)

    # Move
    def updatePosition(self):
        if len(self.directions) > 1:
            self.directions.pop()
        d = self.directions[0]

        new = ((self.positions[0][0] + d[0])%XSIZE, (self.positions[0][1] + d[1])%YSIZE)

        if self.extra <= 0:# if the snake will grow
            self.oldend = self.positions.pop()# Remove tail end
        else:
            self.extra -= 1# get fatter, and but your growth spurt slows :-0
            self.oldend = None# nothing to clear afterwards
        # Add the head
        self.positions.insert(0, new)

        # head,neck,tail,old
        return self.positions[0],self.positions[1],self.positions[-1],self.oldend

    def winAnim(self):# for a possible win anim
        if len(self.positions) > 1:
            self.oldend = self.positions.pop()
            return self.oldend
        else:
            return None

    def getDir(self,a,b):
        if (self.positions[a][0] + 1)%XSIZE == self.positions[b][0]:
           return (1,0)
        if (self.positions[a][0] - 1)%XSIZE == self.positions[b][0]:
            return (-1,0)
        if (self.positions[a][1] + 1)%YSIZE == self.positions[b][1]:
            return (0,1)
        if (self.positions[a][1] - 1)%YSIZE == self.positions[b][1]:
            return (0,-1)

    def getJointDirections(self,k):# Weird as heck
        if k == 0:
            print("HEAD")
            return None,None

        front = self.getDir(k,k-1)
        # for 1, it is s0-s1
        if k == len(self.positions) - 1:
            return front,None
        back = self.getDir(k,k-1)
        return front,back

    # Change self
    def getFatter(self):
        self.extra += 4

    def setWinMode(self,win):# REMOVE
        self.won = win

    def editorClear(self):
        self.positions = []
        self.directions = []# UP

    def editorAdd(self, spos):
        self.positions.insert(0, spos)
        if len(self.positions) > 1:
            self.directions = [(self.positions[0][0] - self.positions[1][0], self.positions[0][1] - self.positions[1][1])]
        else:
            self.directions = [(0,-1)]

if __name__ == "__main__":
    print("Be amazed. Be very amazed.")
    quit()