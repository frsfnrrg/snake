# -*- coding: utf-8 -*-
import pygame
from snakeCode.constants import *
from snakeCode.colors import colors
from snakeCode.object import Object

class textbox(Object):
    # EXTENDABLE_TEXTBOX and FIXED_TEXTBOX
    def __init__(self, length, fontcolor, bgcolor, extendable):# length is in pixels
        self.xsize = length
        self.ysize = BUTTON_HEIGHT
        if self.xsize < 1:
            raise Warning("Not enough space: negative or zero length given")
        self.I = pygame.Surface( (self.xsize, self.ysize))
        self.bgcolor,self.fontcolor = bgcolor,fontcolor
        self.I.fill(self.bgcolor)

        self.extendable = extendable# TODO implement this: if true, the size wraps to the text length (with a 4,4 buffer)
        self.settext("")

    def setlength(self, length):# This is a function used by SuperPanel: the length is externally adjustable
        #
        self.xsize = length
        self.I = pygame.Surface( (self.xsize, self.ysize))
        self.I.fill(self.bgcolor)
        self.settext(self.text)
        # WARNING Do not change without resetting position

    def __repr__(self):#what the print function uses
        return self.__str__()
    def __str__(self):
        return "<Textbox: >> "+self.text+" <<  with size ("+str(self.xsize)+","+str(self.ysize)+") at pos ("+str(self.xpos)+","+str(self.ypos)+")>"

    def read(self):
        return self.text

    def settext(self, text):# Woe unto those who write too large
        self.text = text
        t = MEDIUM_FONT.render(self.text, True, self.fontcolor)
        tx,ty = t.get_size()

        if self.extendable:
            self.xsize = tx + 5
            self.I = pygame.Surface( (self.xsize, self.ysize))# this is to be centered

        self.I.fill(self.bgcolor)
        self.I.blit(t, ((self.xsize - tx)//2, (self.ysize - ty)//2))

class inputbox(Object):
    def __init__(self, length, fontcolor, bgcolor, title):
        self.xsize = length
        self.ysize = BUTTON_HEIGHT
        self.bgcolor,self.fontcolor = bgcolor,fontcolor
        self.state = 0

        passive = pygame.Surface( (self.xsize, self.ysize))
        passive.fill(scale(self.bgcolor,1))

        clicked = pygame.Surface( (self.xsize, self.ysize))
        clicked.fill(scale(self.bgcolor,.5))

        writing = pygame.Surface( (self.xsize, self.ysize))
        writing.fill(scale(self.bgcolor,.8))

        self.I = [passive, clicked, writing, clicked]# Note pointer link between [1] and [3]

        self.settext("")

        self.title = title

    def __str__(self):
        return "<Inputtextbox: >> "+self.text+" <<  with size ("+str(self.xsize)+","+str(self.ysize)+") at pos ("+str(self.xpos)+","+str(self.ypos)+")>"

    def enable(self):
        self.state = 2

    def image(self):
        return self.I[self.state]

    def disable(self):
        self.state = 0

    def settext(self, text):# Woe unto those who write too large
        self.text = text
        # this, once, failed because "Text has zero width"
        # but it renders _nothing_ fine!
        t = MEDIUM_FONT.render(self.text, True, self.fontcolor)
        tx,ty = t.get_size()

        self.I[0].fill(scale(self.bgcolor,1))
        self.I[0].blit(t, ((self.xsize - tx)//2, (self.ysize - ty)//2))

        self.I[1].fill(scale(self.bgcolor,.5))# SHOULD link to I[3]
        self.I[1].blit(t, ((self.xsize - tx)//2, (self.ysize - ty)//2))

        self.I[2].fill(scale(self.bgcolor,.8))
        self.I[2].blit(t, ((self.xsize - tx)//2, (self.ysize - ty)//2))

    def setlength(self, length):# This is a function used by SuperPanel: the length is externally adjustable
        self.xsize = length
        for i in range(3):
            self.I[i] = pygame.Surface( (self.xsize, self.ysize))
        self.I[3] = self.I[1]
        self.settext(self.text)

    def write(self, char):
        if char == None:
            self.settext(self.text[0:-1])
        elif char == False:
            self.settext("")
        else:
            self.settext(self.text + char)

    def name(self):
        return self.title

    def read(self):
        return self.text

    def click(self, down, pos):
        # c - had clicked on button
        # u - unclicked on button

        if self.xpos <= pos[0] < self.xpos+self.xsize and self.ypos <= pos[1] < self.ypos+self.ysize:
            if down == False and self.state in (1,3):
                self.state = (self.state + 1)%4
                return True, True

            elif down == True and self.state in (0,2):
                self.state += 1
                return True, False
        else:
            if down == False and self.state in (1,3):
                self.state -= 1
                return True, False
        return False, False


def scale(color, value):
    c = [int(value*color[0]),int(value*color[1]),int(value*color[2])]
    for i in c:
        if i > 255:
            i = 255
    return c