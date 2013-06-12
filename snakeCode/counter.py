# -*- coding: utf-8 -*-

import pygame
from snakeCode.button import button
from snakeCode.constants import *
from snakeCode.object import Object
#
#A counter has the general form:
#
#\----------------------------------------------\
#\          \----\ \----\ \----\  \------------\\
#\    k     \SOME\3\NUM-\3\BER \10\ DESCRIPTOR \\
#\          \----\ \----\ \----\  \------------\\
#\----------------------------------------------\



class counter(Object):

    def __init__(self, initialvalue, digits, label, labelcolor, C):
        self.lastcount = ""# empty string
        self.digitcapacity = digits
        self.count = initialvalue
        self.count %= 10**(self.digitcapacity)# just to be sure
        self.label = label
        title = button(self.label, labelcolor, PASSIVE_BUTTON)

        self.numbers = []
        widest = 0
        for i in range(10):
            self.numbers.append(button(str(i), labelcolor, PASSIVE_BUTTON))
            x,y = self.numbers[i].getsize()
            if x > widest:# just to be sure
                widest = x# then again, they are all the same size in the default font
        self.numberspace = widest + 3

        self.xsize = 3 + self.digitcapacity*(self.numberspace) + 7 + title.getlength()
        self.ysize = 36# the height of the buttons

        self.backgroundcolor = C.header
        self.counterimage = pygame.Surface( (self.xsize,self.ysize) )
        self.counterimage.fill(self.backgroundcolor)
        self.counterimage.blit(title.image(), (self.xsize - title.getlength(),0))

        # the descriptor is right adjusted, with no buffer (so the actual counter)
        self.update()

    # The traditional access functions. Great idea: make functions in Snake.py that are just Draw(object) and Undraw(object)
    def image(self):
        return self.counterimage

    def __int__(self):
        return self.count

    def __repr__(self):#what the print function uses
        return self.__str__()

    def __str__(self):
        return "<Counter: >>" + self.label + "<< with value of "+str(self.count)+">"

    def __eq__(self, other):
        if type(other) == int:
            return self.count == other
        else:
            return False

    def add(self, value):# __iadd__ somehow messes up
        self.lastcount = self.count
        self.count += int(value)
        self.count %= 10**(self.digitcapacity)
        self.update()

    def subtract(self, value):
        self.lastcount = self.count
        self.count -= value
        self.count %= 10**(self.digitcapacity)
        self.update()

    def reset(self, value):
        self.lastcount = self.count
        self.count = value
        self.count %= 10**(self.digitcapacity)
        self.update()

    def getvalue(self):
        return self.count

    def update(self):# draw digits, check for change so as to minimize exertions
        places = []
        oldstring = " "*(self.digitcapacity - len(str(self.lastcount))) + str(self.lastcount)# make an n digit string
        newstring = " "*(self.digitcapacity - len(str(self.count))) + str(self.count)

        for p in range(self.digitcapacity):
            if oldstring[p] != newstring[p]:
                places.append(p)

        for q in places:
            if newstring[q] == " ":
                pygame.draw.rect(self.counterimage, self.backgroundcolor,  (3 + q*self.numberspace, 0, self.numberspace - 3, 36) )
            else:
                self.counterimage.blit(self.numbers[int(newstring[q])].image(), (3 + q* self.numberspace, 0) )
