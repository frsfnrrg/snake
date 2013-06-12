# -*- coding: utf-8 -*-

class Object():

    # Object requires that:
    # self.xsize, self.ysize be set, preferably in the init
    # self.I be created according to self.xsize, self.ysize
    # self.xpos,self.ypos be set before use
    # self.enabled be set (preferably to true)
    # # Note: some objects override these functions

    def getsize(self):
        return self.xsize,self.ysize
    def getlength(self):
        return self.xsize
    def getheight(self):
        return self.ysize
    def setpos(self, pos ):
        self.xpos,self.ypos = pos
    def getpos(self):
        return self.xpos,self.ypos
    def getrect(self):
        return (self.xpos,self.ypos,self.xsize,self.ysize)
    def undraw(self):
        return [self.getrect()]
    def image(self):
        return self.I
    def images(self):
        return [(self.image(), self.getpos())]
    def disable(self):# supermenu overrides this
        self.enabled = False
    def enable(self):
        self.enabled = True
    def state(self):
        return self.enabled