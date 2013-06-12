import pygame
from snakeCode.constants import *
from snakeCode.colors import GUIColors as C
from snakeCode.menu import ExtensibleMenu
from snakeCode.object import Object

# the passed in sources are generators, that can be passed
# True (+) and False(-) to select the next or previous level in a levelset

class Image(Object):
    def __init__(self, i):
        self.I = i
        self.xsize = i.get_width()
        self.ysize = i.get_height()
    def setImg(self, i):
        self.I = i

class LevelSetScreen(ExtensibleMenu):
    def __init__(self, optb, idb, source):
        self.source = source
        self.path, u = next(self.source)
        scrc = Image(u)

        self.xsize = XSIZE*20
        self.ysize = YSIZE*20
        self.xpos = 0
        self.ypos = 0
        self.I = pygame.Surface((self.xsize, self.ysize))
        pygame.draw.rect(self.I, C.lsbg, (0, 0, self.xsize, self.ysize))

        # the optb go directly above the image: spacing of 20px

        th = optb[0].getheight() + 20 + scrc.getheight()

        bmin = (self.ysize - th) // 2
        bxm = (self.xsize - sum(b.getlength() for b in optb) - 10 * (len(optb) - 1)) // 2
        for b in optb:
            b.setpos((bxm, bmin))
            bxm += b.getlength() + 10

        lmin = optb[0].getheight() + 20 + bmin
        sl = (self.xsize - scrc.getlength())//2
        scrc.setpos((sl ,lmin))

        dk = (scrc.getheight() - optb[0].getheight()) // 2

        idb[0].setpos( (sl - 10 - idb[0].getlength(), lmin + dk) )
        idb[1].setpos( (sl + scrc.getlength() + 10, lmin + dk) )
        
        self.E = [[b] for b in optb + idb + [scrc]]

        for e in self.E:
            e[0].disable()
            self.I.blit(e[0].image(), e[0].getpos())
        self.choice = None

    def setSource(self, source):
        self.source = source
        self.path, u = next(self.source)
        self.E[-1][0].setImg(u)
        self.I.blit(self.E[-1][0].image(), self.E[-1][0].getpos())
        return [(self.E[-1][0].image(), self.E[-1][0].getpos())]

    def getSections(self, rl):
        draw = []
        for rect in rl:
            if rect == (0,0,self.xsize, self.ysize):
                return [(self.I,(0,0))]

            if rect[1] + rect[3] >= self.ysize:
                rect = (rect[0], rect[1], rect[2], self.ysize - rect[1])
            if rect[0] + rect[2] >= self.xsize:
                rect = (rect[0], rect[1], self.ysize - rect[0], rect[3])

            subimage = pygame.Surface((rect[2],rect[3]))
            subimage.blit(self.I, (0,0), rect)
            draw.append((subimage, (rect[0],rect[1])))
        return draw

    def inc(self):
        self.path, u = self.source.send(True)
        self.E[-1][0].setImg(u)
        self.I.blit(self.E[-1][0].image(), self.E[-1][0].getpos())
        return [(self.E[-1][0].image(), self.E[-1][0].getpos())]

    def dec(self):
        self.path, u = self.source.send(False)
        self.E[-1][0].setImg(u)
        self.I.blit(self.E[-1][0].image(), self.E[-1][0].getpos())
        return [(self.E[-1][0].image(), self.E[-1][0].getpos())]

    def refresh(self):
        self.path, u = self.source.send(None)
        self.E[-1][0].setImg(u)
        self.I.blit(self.E[-1][0].image(), self.E[-1][0].getpos())
        return [(self.E[-1][0].image(), self.E[-1][0].getpos())]

    def getpath(self):
        return self.path

    def disable(self):
        self.enabled = False
        draw = []
        for j in self.E:
            for k in j:
                k.disable()
                draw += k.images()
        for a, b in draw:
            self.I.blit(a, b)
        return draw

    def enable(self):
        self.enabled = True
        draw = []
        for j in self.E:
            for k in j:
                k.enable()
                draw += k.images()
        for a, b in draw:
            self.I.blit(a, b)
        return draw
    