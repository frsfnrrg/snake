# -*- coding: utf-8 -*-
import pygame
from pygame.locals import SRCALPHA
from snakeCode.constants import *
from snakeCode.object import Object


class button(Object):
    # mode
    # 0 Plain- can be clicked. Meant to call some external function, say QUIT
    # 1 Passive - these buttons are 100% guarantied to do nothing. they just sit there, plotting your fiery demise
    # 2 Lock - these buttons have a fourth mode - once clicked, they stay depressed until clicked again
    # 3 Item - these lock buttons are inherently part of a vertical selector menu -
    def __init__(self, text, color, mode):

        t = MEDIUM_FONT.render(text, True, color)
        tx,ty = t.get_size()
        self.xsize = tx+10
        self.ysize = BUTTON_HEIGHT
        pos = (self.xsize - tx)//2, (self.ysize - ty)//2
        default = pygame.Surface((self.xsize, self.ysize))# have 48 space, - 2 top rim, - 4 edges, makes 38 space
        default.fill( (100,100,100) )
        default.blit(t, pos)# centered on surface

        if mode != 1:
            clicked = pygame.Surface((self.xsize, self.ysize))
            clicked.fill( (60,60,60) )
            clicked.blit(t, pos)

            disabled = pygame.Surface((self.xsize, self.ysize))# faded-disabled
            overlay = pygame.Surface((self.xsize, self.ysize))
            overlay.fill((100,100,120))
            overlay.set_alpha(200)
            disabled.fill((100,100,100))
            disabled.blit(t, pos)
            disabled.blit(overlay, (0,0))

            if mode == 0:
                self.I = [default, clicked, disabled]
            else:

                held = pygame.Surface((self.xsize, self.ysize))
                held.fill( (80,80,80) )#lighter than clicked, darked than regular
                held.blit(t, pos )
                #               0        1        2      -1
                self.I = [default, clicked, held, disabled]

            self.state = 0# 0-REGULAR,1-CLICKED,-1-DISABLED, 2 HOLD
        else:
            self.I = [default]
            self.state = -1

        self.mode = mode

        self.text = text
        self.position = None
        self.xpos,self.ypos = None,None

    def image(self):
        return self.I[self.state]# note that for number/label buttons, i[-1] == i[0]

    def name(self):# each button is uniquely identified by the text on it. this is what the main loop interprets: the name
        return self.text

    def getstate(self):
        return self.state

    def __repr__(self):
        #use format
        return "<Button: >>" + self.text + "<< with size ("+str(self.xsize)+","+str(self.ysize)+") at pos ("+str(self.xpos)+","+str(self.ypos)+")>"

    def disable(self):
        self.state = -1
    def hold(self):
        self.state = 2
    def release(self):
        self.state = 0

    def enable(self):
        if self.state == -1 and self.mode != 1:# numberbuttons can not escape disabledness
            self.state = 0

    def click(self,down,pos):
        if self.mode == 1 or self.state == -1:# if passive/disabled, do nothing# this is a precaution
        # Question: if passive buttons are always disabled, then why bother doing the self.mode?
            return None,None
        # returns Clickdown, clickup

        if self.xpos <= pos[0] < self.xpos+self.xsize and self.ypos <= pos[1] < self.ypos+self.ysize:
            if down == True and (self.state == 0 or (self.state == 2 and self.mode != 3)):
                self.state = 1
                return True,False# UPDATE,CLICKUP
            if down == False and self.state == 1:
                self.state = 0
                return True,True
            return False,False# mode == disabled-no change
        else:
            if self.state == 1:
                self.state = 0
                return True,False# misclicked
            return False,False# never even clicked there

class toolbutton(button):# extends button: has a different init and thus a different shape
    def __init__(self, letter, textcolor, bgcolor):

        t = BIG_FONT.render(letter, True, textcolor)
        tx,ty = t.get_size()

        default = pygame.Surface((TOOLBUTTON_SIZE,TOOLBUTTON_SIZE))
        default.fill(scale(bgcolor, 1))
        default.blit(t, ((TOOLBUTTON_SIZE - tx)//2,(TOOLBUTTON_SIZE - ty)//2))

        clicked = pygame.Surface((TOOLBUTTON_SIZE,TOOLBUTTON_SIZE))
        clicked.fill(scale(bgcolor, .5))
        clicked.blit(t, ((TOOLBUTTON_SIZE - tx)//2,(TOOLBUTTON_SIZE - ty)//2))

        held = pygame.Surface((TOOLBUTTON_SIZE,TOOLBUTTON_SIZE))
        held.fill(scale(bgcolor, .8))
        held.blit(t, ((TOOLBUTTON_SIZE - tx)//2,(TOOLBUTTON_SIZE - ty)//2))

        disabled = pygame.Surface((TOOLBUTTON_SIZE,TOOLBUTTON_SIZE))
        disabled.fill(scale(bgcolor, 1))
        disabled.blit(t, ((TOOLBUTTON_SIZE - tx)//2,(TOOLBUTTON_SIZE - ty)//2))
        overlay = pygame.Surface((TOOLBUTTON_SIZE,TOOLBUTTON_SIZE))
        overlay.fill((100,100,120))
        overlay.set_alpha(200)
        disabled.blit(overlay, (0,0))

        self.I = [default, clicked, held, disabled]
        self.mode = PLAIN_BUTTON
        self.state = 0
        self.text = letter
        self.xsize = TOOLBUTTON_SIZE
        self.ysize = TOOLBUTTON_SIZE
        self.position = None
        self.xpos,self.ypos = None,None

class tributton(button):
    def __init__(self, name, width, height, right):
        default = tributton._drawTri(right, height, width, (100,100,100,255))
        clicked = tributton._drawTri(right, height, width, (60,60,60,255))

        disabled = tributton._drawTri(right, height, width, (100,100,100,255))
        overlay = tributton._drawTri(right, height, width, (100,100,120,200))
        disabled.blit(overlay, (0,0))
        # draw tri
        
        
        # held is irrelevant
        #           0        1        -1
        self.I = [default, clicked, disabled]

        self.mode = PLAIN_BUTTON
        self.text = name
        self.state = 0
        self.xsize = width
        self.ysize = height
        self.position = None
        self.xpos,self.ypos = None,None
        self.right = right

    def click(self,down,pos):
        # TODO reduce click area to the triangle
        if self.xpos <= pos[0] < self.xpos+self.xsize and self.ypos <= pos[1] < self.ypos+self.ysize:
            if down == True and self.state == 0:
                self.state = 1
                return True,False# UPDATE,CLICKUP
            if down == False and self.state == 1:
                self.state = 0
                return True,True
            return False,False# mode == disabled-no change
        else:
            if self.state == 1:
                self.state = 0
                return True,False# misclicked
            return False,False# never even clicked there


    def _drawTri(right, height, width, color):
        s = pygame.Surface((width, height), flags=SRCALPHA)
        s.fill((0,0,0,0))
        
        if right:
            r = [(0,0), (width, height//2), (0, height)]
        else:
            r = [(width,0), (0, height//2), (width, height)]
        pygame.draw.aalines(s, color, True, r)
        pygame.draw.polygon(s, color, r)

        return s


def scale(color, value):
    c = [int(value*color[0]),int(value*color[1]),int(value*color[2])]
    for i in c:
        if i > 255:
            i = 255
    return c