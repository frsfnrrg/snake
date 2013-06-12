# -*- coding: utf-8 -*-
import pygame
from snakeCode.constants import *
from snakeCode.colors import GUIColors as C
from snakeCode.menu import Menu

# The sidebar does NOT extend into the real world. It is a simple selector.
# When disabled, what it has selected is NOT lost

class Sidebar(Menu):# 60 pixels wide
    def __init__(self, buttons):

        self.xsize = 60
        self.ysize = YSIZE*20

        self.I = pygame.Surface((self.xsize, self.ysize))
        self.I.fill(C.header)
        pygame.draw.rect(self.I, C.headerrim, (0,0,2,self.ysize))
        pygame.draw.rect(self.I, C.headerrim, (2,0,self.xsize-2,2))

        ypos = 6
        xpos = 6
        self.E = buttons
        for b in self.E:
            b.setpos((xpos, ypos))
            self.I.blit(b.image(), b.getpos())
            ypos += b.getsize()[1] + 6

        self.choice = None# nothing selected yet
        self.enabled = True# can be disabled when testing or otherwise

    def __repr__(self):
        return "<Side Toolbar: with size ("+str(self.xsize)+","+str(self.ysize)+") on the right side and "+len(self.E)+" objects.>"

    def disable(self):# disable all the buttons
        r = []
        for B in self.E:
            B.disable()
            self.I.blit(B.image(), B.getpos())
            r.append((B.image(), B.getpos()))
        self.enabled = True
        # we do not reset the choice
        r = self._drawadjust(r)
        return r

    def select(self, number):
        r = []
        if self.choice != None:
            self.E[self.choice].release()
            self.I.blit(self.E[self.choice].image(), self.E[self.choice].getpos())
            r.append((self.E[self.choice].image(), self.E[self.choice].getpos()))
        self.choice = number
        self.E[self.choice].hold()
        self.I.blit(self.E[self.choice].image(), self.E[self.choice].getpos())
        r.append((self.E[self.choice].image(), self.E[self.choice].getpos()))
        r = self._drawadjust(r)
        return r

    def enable(self):
        r = []
        if self.choice != None:
            self.E[self.choice].hold()
            # the button will be reblit anyway in the next step

        for B in self.E:
            B.enable()
            self.I.blit(B.image(), B.getpos())
            r.append((B.image(), B.getpos()))
        self.enabled = True
        r = self._drawadjust(r)
        return r

    def click(self, state, pos):# This thing IS a selector menu, just with different setup
        # returns draw, [], command
        # the middle is undraw, but that is never used, save for uniformity of access
        if not self.enabled:
            return [], [], None

        for b in range(len(self.E)):# in all buttons

            c, u = self.E[b].click(state, self._clickshift(pos))
            if c == True:# Had it been clicked on
                if u == True:# Was it unclicked on the button
                    if self.choice == None:
                        raise Warning# A choice needs to have been selected

                    self.E[b].hold()
                    self.E[self.choice].release()

                    self.I.blit(self.E[b].image(),  self.E[b].getpos())
                    self.I.blit(self.E[self.choice].image(),  self.E[self.choice].getpos())

                    draw = self.E[b].images() + self.E[self.choice].images()
                    self.choice = b
                    return self._drawadjust(draw), [], self.E[self.choice].name()# ###
                else:# Nothin changed
                    self.E[self.choice].hold()
                    return self._drawadjust(self.E[b].images()), [], False


        return [], [], None# returns draw, udraw, command# ###