# -*- coding: utf-8 -*-
import pygame
from snakeCode.constants import *
from snakeCode.object import Object
from snakeCode.colors import GUIColors as C

from snakeCode.menu import *
from snakeCode.textbox import textbox, inputbox# For type comparisons
from snakeCode.counter import counter
from snakeCode.button import button


# The menu system is like a nested retrieval system: clicks go through all layers, and each sends down or acts
# on that which is sent it, and returns all the info which is to be sent out : images, positions, rects, commands
# each part is only aware of what is above and below it on the chain of commands

class Menu(Object):# the generic menu set of functions

    # exterior methods
    def __init__(self):
        self.xsize = self.ysize = 1
        self.I = pygame.Surface((self.xsize, self.ysize))
    # menus have one form of image return (Object), and can be undrawn
    def undraw(self):
        return [self.getrect()]

    def remoteSet(self, path, choice):
        return self.setchoice(choice)

    def setbounds(self, left, right):# The horizontal boundaries of a menu's subspace
    # THese a spacefillers unless one is Extensible or future something
        self.lbound = left - self.xpos
        self.rbound = right - self.xpos

    # Interior methods
    def _inside(self, pos):
        if self.xpos <= pos[0] < self.xpos + self.xsize:
            if self.ypos <= pos[1] < self.ypos + self.ysize:
                return True
        return False

    def _drawadjust(self, draw):
        for i in range(len(draw)):
            draw[i] = (draw[i][0], (draw[i][1][0]+self.xpos,draw[i][1][1]+self.ypos))
        return draw
    # so far only for supermenu, and footer with floating subobjects could need this
    def _udrawadjust(self, udraw):
        for i in range(len(udraw)):
            udraw[i] = (udraw[i][0]+self.xpos,udraw[i][1]+self.ypos, udraw[i][2], udraw[i][3])
        return udraw

    def _clickshift(self, pos):
        return (pos[0] - self.xpos, pos[1] - self.ypos)



# The usual selector menu. It holds a set of buttons, which are clicked to choose one of them. These can
# only have one entry selected at a time, and can not be fed new information

class SelectorMenu(Menu):
    def __init__(self, E, C):
        # entries: the buttons being passed to the menu, in order. vertical, the default, implemented menu type
        # C the colorset being passed to the menu

        self.E = E# the list of entries
        self.enabled = False# on create, the menu is not in use

        self.choice = 0
        # create menu, give buttons positions, etc

        self.xsize = 0
        self.ysize = 0

        for b in self.E:# find dimensions
            x,y = b.getsize()
            if x > self.xsize:
                self.xsize = x
            self.ysize += y + 2

        self.xsize += 8#buffer and rim
        self.ysize += 4
        self.I = pygame.Surface((self.xsize,self.ysize))
        self.I.fill(C.headerrim)
        pygame.draw.rect(self.I, C.header, (2,2,self.xsize-4,self.ysize-4))# 2 pixel buffer

        yp = 3
        for b in self.E:
            x,y = b.getsize()
            b.setpos( ((self.xsize-x)//2, yp) )
            self.I.blit(b.image(),  b.getpos())
            yp += 2 + y

    def __repr__(self):
        return "<Selector Menu: with size ("+str(self.xsize)+","+str(self.ysize)+") at pos ("+str(self.xpos)+","+str(self.ypos)+")>"

    # Remote select an option
    def setchoice(self, choice):

        oldchoice = self.choice
        self.choice = choice

        self.E[oldchoice].release()
        self.E[self.choice].hold()# hold  the one wnated

        self.I.blit(self.E[oldchoice].image(),  self.E[oldchoice].getpos())
        self.I.blit(self.E[self.choice].image(),  self.E[self.choice].getpos())
        if self.enabled:# only return images if enabled

            # that which has been changed
            draw = [(self.E[self.choice].image(),  self.E[self.choice].getpos()),(self.E[oldchoice].image(),  self.E[oldchoice].getpos())]
            return self._drawadjust(draw)

        return []

    #Click handling
    def click(self, state, pos):

        if not self.enabled:
            return [], [], None

        for b in range(len(self.E)):
            # 2pressed button; 2released button
            c, u = self.E[b].click(state, self._clickshift(pos))
            if c == True:
                if u == True:# if
                    self.E[b].hold()
                self.I.blit(self.E[b].image(),  self.E[b].getpos())
                draw = [(self.E[b].image(),  self.E[b].getpos())]

                if u == True:
                    for B in range(len(self.E)):# clear others: only do so in u is true? false?
                        if B != b and self.E[B].getstate() == 2:
                            self.E[B].release()
                            self.I.blit(self.E[B].image(),  self.E[B].getpos())
                            draw.append(  (self.E[B].image(),  self.E[B].getpos())   )
                        elif self.E[B].getstate == 2:
                            return self._drawadjust(draw), [], None# Same: nothing happened

                self.choice = b# select clicked button
                #      draw udraw       command
                return self._drawadjust(draw), [], self.E[self.choice].name()# return the button name that was pressed

        return [], [], None# returns draw, udraw, command


# ListMenu: this thing is there to choose from a very extendable list, with information being delivered from
# the outside via setchoice ( (number, supertext, subtext)). if number == None, there is just a text delivery
# The numerical sum values in the init are seperated into constituent parts for clarity

class ListMenu(Menu):# TODO Make it so an iterator is passed to this function, with next() and previous() methods. Then it returns only values
    def __init__(self, name, length, textcolor, C, iterator=None):
        self.title = name
        self.enabled = False
        self.ysize = 8 + 2 * BUTTON_HEIGHT
        self.xsize = length

        self.source = iterator

        self.I = pygame.Surface((self.xsize, self.ysize))
        self.C = C
        self.I.fill(self.C.headerrim)
        pygame.draw.rect(self.I, self.C.header, (2,2,self.xsize-4,self.ysize-4))# 2 pixel buffer

        #R button and L button
        self.buttons = [
            button("<<", textcolor, PLAIN_BUTTON),
            button(">>", textcolor, PLAIN_BUTTON),
        ]

        self.buttons[0].setpos(( 3, 3 ))
        self.buttons[1].setpos((self.xsize - 3 - self.buttons[1].getlength(), 3  ))

        for i in range(2):
            self.I.blit(self.buttons[i].image(), self.buttons[i].getpos())

        #               total   ends            button1          b1space    button2              b2space
        smallerlength = self.xsize - 6 - self.buttons[0].getlength() - 3 - self.buttons[1].getlength() - 3
        largerlength = self.xsize - 6

        self.textboxes = [
            textbox(smallerlength, textcolor, self.C.textboxbg, FIXED_TEXTBOX),
            textbox(largerlength, textcolor, self.C.textboxbg, FIXED_TEXTBOX)
        ]

        self.textboxes[0].setpos((6 + self.buttons[0].getlength(), 3 ))
        self.textboxes[1].setpos((3, 5 + BUTTON_HEIGHT ))\

        if self.source != None:
            self.source_ret = next(self.source)
            self.setchoice(self.source_ret[:2])

    def __repr__(self):
        return "<List Menu: with size ("+str(self.xsize)+","+str(self.ysize)+") at pos ("+str(self.xpos)+","+str(self.ypos)+")>"

    def setchoice(self, values):# values is ["topstr", "bottomstr"]
        for i in range(2):
            self.textboxes[i].settext(values[i])
            self.I.blit(self.textboxes[i].image(), self.textboxes[i].getpos())

        if self.enabled:# return images if on
            draw = [(self.textboxes[0].image(), self.textboxes[0].getpos()),(self.textboxes[1].image(), self.textboxes[1].getpos())]
            return self._drawadjust(draw)
        return []

    def setsource(self, iterator):
        self.source = iterator
        self.setchoice(next(self.source)[:2])
        if self.enabled:# return images if on
            draw = [(self.textboxes[0].image(), self.textboxes[0].getpos()),(self.textboxes[1].image(), self.textboxes[1].getpos())]
            return self._drawadjust(draw)
        return []

    def remoteSet(self, path, choice):
        if len(path) > 0:
            raise Doomsicle("No submenus")
        if type(choice) == list:
            return self.setchoice(choice)
        else:# passing in a generator
            return self.setsource(choice)


    def remoteRead(self, path):
        if len(path) > 0:
            raise Doomsicle("Has no submenus")
        if self.source == None:
            return [i.read() for i in self.textboxes]
        else:
            return self.source_ret[2]

    def click(self, state, pos):# the primary function
        if not self.enabled:
            return [],[],None

        ret = None
        for i in range(2):# only two buttons to deal with
            c,u = self.buttons[i].click(state, self._clickshift(pos) )
            if c:
                if u:
                    ret = self.buttons[i].name()
                self.I.blit(self.buttons[i].image(), self.buttons[i].getpos())
                draw = [(self.buttons[i].image(),self.buttons[i].getpos())]

                if ret != None:
                    if self.source == None:
                        return self._drawadjust(draw), [], self.title + "." + ret# so menu MONKEY and decrementbutton makes MONKEY.<<
                    else:# Generators are wonderful things
                        self.source_ret = self.source.send({">>":True,"<<":False}[ret])# Tell the souce to increase/decrease, and returns its result
                        draw = self._drawadjust(draw)

                        draw += self.setchoice(self.source_ret[:2])
                        return draw, [], "NAME" + "." + self.source_ret[2]

                else:
                    return self._drawadjust(draw), [], None

        return [],[],None

class ExtensibleMenu(Menu):# Can have any number of things attached to it or in it.

    def click(self, state, pos):# The ultimate click function

        for a in range(len(self.E)):#
            # How items are to be handled depends on type:
            # There are three->four categories
            # menus# which extend
            # simple buttons# which click
            # textboxes, counters# which display
            # inputtextboxes# which receive input

            if len(self.E[a]) == 2: # MENU CASE: click self
                #  c - had been pressed on button
                #  u - had been depressed on button
                #
                c,u = self.E[a][0].click(state, self._clickshift(pos))# clicking in the buttons' global coordinates
                if c:
                    flag, udraw = None, []
                    if u:
                        if self.choice != a:
                            self.E[a][0].hold()
                            # enable, relay name draw command
                            self.E[a][1].enable()# turn the lower level menu on

                            # undo all the other menus: add a rect to the undraw list
                            if self.choice != None:
                                flag = self.choice
                                if len(self.E[self.choice]) == 2:
                                    self.E[self.choice][0].release()
                                    self.I.blit(self.E[self.choice][0].image(), self.E[self.choice][0].getpos())
                                    # order matters: disable closes the submenu
                                    udraw = self.E[self.choice][1].undraw()# things that collapse when this menu does
                                    self.E[self.choice][1].disable()

                                elif type(self.E[self.choice][0]) == inputbox:
                                    self.E[self.choice][0].disable()# image already dealt with

                            self.choice = a
                        else: # clicking on the already chosen button
                            flag = -1
                            self.E[a][0].release() # release the button otherwise
                            self.choice = None
                            udraw = self.E[a][1].undraw()
                            self.E[a][1].disable()
                    self.I.blit(self.E[a][0].image(), self.E[a][0].getpos())# draw the updated image, on the self

                    # Case 1: the menu is undrawn, the menu button updates
                    # Case 2: the menu is drawn, the menu button updates
                    # Case 3: the menu switches, drawing a menu, updating two buttons
                    if flag == -1:#Case 1
                        draw = [(self.E[a][0].image(), self.E[a][0].getpos())]
                    elif flag == None:# Case 2
                        draw = [(self.E[a][0].image(),self.E[a][0].getpos()),(self.E[a][1].image(), self.E[a][1].getpos())]
                    else:#Case 3
                        draw = [(self.E[a][0].image(),self.E[a][0].getpos()),(self.E[a][1].image(), self.E[a][1].getpos()),(self.E[flag][0].image(), self.E[flag][0].getpos())]


                    return self._drawadjust(draw), self._udrawadjust(udraw), None

            # how do I duck type this? Or make all such objects subclass a "FixedInteractableObject" class, and others a "FloatingInteractable"
            elif type(self.E[a][0]) == inputbox or isinstance(self.E[a][0], button):# Buttons to be clicked
                c,u = self.E[a][0].click(state, self._clickshift(pos))# CLICK
                if c:
                    draw = [(self.E[a][0].image(), self.E[a][0].getpos())]
                    udraw = []
                    self.I.blit(self.E[a][0].image(), self.E[a][0].getpos())# draw the updated image, on the self
                    if u:
                        # undraw old menus
                        if self.choice != None:
                            if len(self.E[self.choice]) == 2:# We have a menu
                                #order matters
                                self.E[self.choice][0].release()
                                self.I.blit(self.E[self.choice][0].image(), self.E[self.choice][0].getpos())
                                udraw += self.E[self.choice][1].undraw()# get rid of floating appendage
                                self.E[self.choice][1].disable()
                                draw += self.E[self.choice][0].images()
                            elif type(self.E[self.choice][0]) == inputbox:
                                self.E[self.choice][0].disable()
                                draw += self.E[self.choice][0].images()

                        if type(self.E[a][0]) == inputbox and self.choice != a:#
                            self.choice = a
                        else:# Button case, or same textbox
                            self.choice = None
                        return self._drawadjust(draw), self._udrawadjust(udraw), self.E[a][0].name()
                    return self._drawadjust(draw), self._udrawadjust(udraw), None

        if self.choice != None and len(self.E[self.choice]) == 2: # ask open submenu: pass it on
            draw, udraw, command = self.E[self.choice][1].click(state, self._clickshift(pos))# CLICK non-menu
            # question. How to balance with clicking on a textbox?

            return self._drawadjust(draw), self._udrawadjust(udraw), command

        return [], [], None

    def remoteSet(self, path, choice):
        w = path[0]
        del path[0]

        # returns IMAGES, RECTS(local)
        if len(self.E[w]) == 2:
            return self._drawadjust(self.E[w][1].remoteSet(path, choice)), []# the selector menus just ignore the path :-)

        elif type(self.E[w][0]) == button:
            if choice == True:# HOLD
                self.E[w][0].enable()
            elif choice == False:
                self.E[w][0].disable()
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            return [], self._udrawadjust([self.E[w][0].getrect()])

        elif type(self.E[w][0]) == textbox:
            self.E[w][0].settext(choice)
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            return [], self._udrawadjust([self.E[w][0].getrect()])


        elif type(self.E[w][0]) == inputbox:
            self.E[w][0].settext(choice)
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            return [], self._udrawadjust([self.E[w][0].getrect()])

        else:
            print(type(self.E[w][0]), "remoteSet: type not accounted for")
            raise Doomsicle("Evil laugh.")

    # read a value from some object
    def remoteRead(self, path):
        w = path[0]
        del path[0]

        if type(self.E[w][0]) == inputbox:
            return self.E[w][0].read()
        elif len(self.E[w]) == 2:
            return self.E[w][1].remoteRead(path)

    def remoteWrite(self, char):
        if type(self.E[self.choice][0]) == inputbox:
            self.E[self.choice][0].write(char)
            self.I.blit(self.E[self.choice][0].image(), self.E[self.choice][0].getpos())
            return [], [self.E[self.choice][0].getrect()]# what to update

        elif len(self.E[self.choice]) == 2:# remote read and remote write should go along the chain of open stuff to an open textbox object
            pass

    def remoteSetSource(self, path, iterator):
        pass

    def getOpen(self):
        if self.choice != None:
            return self.E[self.choice][0].name()
        return None
# Behold the Supermenu. It takes a list of menus, and does for them as for the options menu
# When ever it updates something, it creates a rect to pass on, as its submenus should
# it passes on clicks to its sub-menus, and recieves an action code (the button name) from a selector menu or something
# Works fine, as long as all subentries are uniquely named

# to move coordinates for level B to A where A > B: b.x += a.xpos,b.y += a.ypos . subtract to move down again

class SuperMenu(ExtensibleMenu):

    def __init__(self, E, C):
        # E (entries) is [    (xmenu, button), (xmenu, button), (xmenu,button) ..... ]
        # the menus may be any menuobject - selectormenu or supermenu or (inevitably) countermenu/choicemenu
        # background color and rimcolor are the usual defaults
        # C (color) is the color set. C.header and C.headerrim are used

        self.enabled = False# menus begin as default off
        self.xsize = -4# 2 (1,x,5), (5,x,5), ... (5,x,1) 2
        self.ysize = 6 + BUTTON_HEIGHT# 2 (1,x,1) 2
        self.E = E

        for subset in self.E:
            x,y = subset[0].getsize()
            self.xsize += 10 + x# 5 buffer

        self.I = pygame.Surface((self.xsize,self.ysize))# the block that is the self
        self.I.fill(C.headerrim)
        pygame.draw.rect(self.I, C.header, (2,2,self.xsize-4,self.ysize-4))
        # draw on all the buttons

        x = 3
        for item in self.E:
            item[0].setpos((x,3))# give the button its place
            self.I.blit(item[0].image(), item[0].getpos())# and the sub-menu buttons are created

            #negative coordinates are fine: all clicks, positions, will be normalized
            x += 10 + item[0].getlength()

        self.choice = None# which one of the submenus is active

    def setbounds(self, left, right):# To ensure all submenus stay on screen

        self.lbound = left - self.xpos# Localise
        self.rbound = right - self.xpos

        for item in self.E:
            if len(item) == 2:
                xm,ym = item[1].getsize()
                x = item[0].getpos()[0]
                xb = item[0].getlength()
                X = x + (xb - xm)//2
                if X < self.lbound:
                    X = self.lbound
                elif X + xb > self.rbound:
                    X = self.rbound - xb
                elif xb > self.rbound - self.lbound:
                    raise Warning("The submenu is wider than its allowed zone. Shrink it.")

                item[1].setpos((X, -ym))#put the menu centered over the button and directly above this menu
                item[1].setbounds(self.lbound, self.rbound)

    def images(self):# that which should be drawn, with its globalized position. This procedure only gets all the visible menus left
        if self.choice == None or len(self.E[self.choice]) == 1:
            return [(self.I, self.getpos())]
        return [(self.I, self.getpos())] + self._drawadjust(self.E[self.choice][1].images())# those images which need to be drawn, with the positions.

    def undraw(self):
        if self.choice == None:
            return [self.getrect()]
        return [self.getrect()] + self._udrawadjust(self.E[self.choice][1].undraw())# the rectangles which need to be undrawn

    # ON/OFF
    def disable(self):
        self.enabled = False

        if self.choice != None:
            self.E[self.choice][0].release()# release the button below, and draw the change
            self.I.blit(self.E[self.choice][0].image(), self.E[self.choice][0].getpos())

            self.E[self.choice][1].disable()# turn off the menu below

        self.choice = None

    def remoteSet(self, path, choice):
        w = path[0]
        del path[0]

        # here we return
        # DRAW
        # UPDATE# ARG, the curses of having one blit to reality and the other to doublebuffer

        if len(self.E[w]) == 2:
            draw = self.E[w][1].remoteSet(path, choice)# the selector menus just ignore the path :-)

        elif type(self.E[w][0]) == button:
            if choice == True:# HOLD
                self.E[w][0].enable()
            elif choice == False:
                self.E[w][0].disable()
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            draw = self.E[w][0].getimages(),

        elif type(self.E[w][0]) == textbox:
            self.E[w][0].settext(choice)
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            draw = self.E[w][0].getimages()

        elif type(self.E[w][0]) == inputbox:
            self.E[w][0].write(choice)
            self.I.blit(self.E[w][0].image(), self.E[w][0].getpos())
            draw = self.E[w][0].getimages()

        if self.enabled == False:
            return []# nothing if disabled

        return self._drawadjust(draw)


# This is an always on panel designed for the bottom of the screen
# This panel is designed to work both for the Level Editor, The
# It links to the self.screen object of the main file.
# It accepts a collection of objects: right adjusted, left adjusted, extensible, etc.

# screen: pygame screen object
# EXAMPLE args
# leftset = [  [button], [button, selectormenu],  [button, supermenu]   ]
# extensible = [  [stretchy textbox object] ]
# rightset = [ [inputtextbox],    [button, listmenu], [button], [button] ]

class SuperPanel(ExtensibleMenu):
    def __init__(self, screen, leftset, extensible, rightset):
        self.I = screen# this links the screen into this: No (some) adjusting needed
        # This should boost speed. Nothing writes over the SuperPanel anyway
        self.xsize = screen.get_size()[0]# Pygame function
        self.ysize = 4 + BUTTON_HEIGHT# == 40, 2 + 2 + 36
        pygame.draw.rect(self.I, C.header, (0, YSIZE*20+2, self.xsize, self.ysize - 2))
        pygame.draw.rect(self.I, C.headerrim, (0, YSIZE*20, self.xsize, 2))

        # PLace leftset

        ypos = YSIZE * 20 + 4
        lxpos = 5

        for item in leftset:# Placement is by item[0]
            item[0].setpos((lxpos,ypos))# The button/obj
            self.I.blit(item[0].image(), item[0].getpos())

            if len(item) == 2:# Houston, we have a menu.
                self._placeMenu(item, lxpos)

            lxpos += item[0].getlength() + 10

        #Place rightset

        rxpos = XSIZE*20 + 60 - 5

        for i in range(len(rightset)-1,-1,-1):# Iterate through in reverse order, so final set || actual positions
            rxpos -= rightset[i][0].getlength()
            rightset[i][0].setpos((rxpos,ypos))# The button/obj
            self.I.blit(rightset[i][0].image(), rightset[i][0].getpos())

            if len(rightset[i]) == 2:# Houston, we have a menu.
                self._placeMenu(rightset[i], rxpos)

            rxpos -= 10
        # If exists, place and setlength() the extensible center object

        if len(extensible) != 0:

            length = (rxpos-lxpos + 10 - len(extensible)*10)//len(extensible)
            mxpos = lxpos
            for item in extensible:
                item[0].setlength(length)
                item[0].setpos((mxpos,ypos))
                self.I.blit(item[0].image(), item[0].getpos())
                mxpos += 10 + length

        self.E = leftset + extensible + rightset# set concatenation

        self.xpos, self.ypos = 0,0# These are the coordinates of the current reference frame
        self.choice = None# Can be a menu or an inputtextbox

    def _placeMenu(self, item, xp):
        x = xp + (item[0].getlength() - item[1].getlength())//2
        if x < 0:# We need _some_ bounds
            x = 0
        elif x + item[0].getlength() > XSIZE*20:
            x = XSIZE*20 - item[0].getlength()
        elif item[0].getlength() > XSIZE*20:
            raise Warning("The submenu is wider than its allowed zone. Shrink it.")
        item[1].setpos((x, YSIZE*20 - item[1].getheight()))
        item[1].setbounds(0, XSIZE*20)

# --------------------- REMOTES -------------------------------

    # These are seperate from set: value and enabledness are different
    def remoteDisable(self, i=None):
        if i != None:# an explicit thing, like a button
            self.E[i][0].disable()
            return self.E[i][0].images(), []
        if self.choice != None:
            if len(self.E[self.choice]) == 1:
                self.E[self.choice][0].disable()
                draw = self.E[self.choice][0].images()
                self.choice = None
                return draw, []
            else:
                self.E[self.choice][0].release()# button
                self.E[self.choice][1].disable()# menu
                draw, udraw = self.E[self.choice][0].images(), self.E[self.choice][1].undraw()
                self.choice = None
                return draw, udraw
        return [],[]#draw, undraw

    def remoteEnable(self, objectnumber):# this definately needs a number
        self.E[objectnumber][0].enable()
        return self.E[objectnumber][0].images(), self.E[objectnumber][0].undraw()

    def remoteImages(self, objectnumber):
        if len(self.E[objectnumber]) == 1:
            return self.E[objectnumber][0].images()
        else:
            return self.E[objectnumber][1].images()

    def isAnythingOpen(self):
        if self.choice != None:
            return True
        return False

    def closeAll(self):
        update = []# rectlist
        if self.choice != None:
            if len(self.E[self.choice]) == 2:# menu
                self.E[self.choice][1].disable()
                self.E[self.choice][0].release()
            else:# inputbox
                self.E[self.choice][0].disable()
            self.I.blit(self.E[self.choice][0].image(), self.E[self.choice][0].getpos())
            update = [self.E[self.choice][0].getrect()]
            self.choice = None
        return self.undraw(), update

# -------------------- DRAWING/UNDRAWING --------------------------------------------------

# THere is NO displacement: this is THE reference frame, the SELF is never drawn

    def images(self):# that which should be drawn, with its globalized position. This procedure only gets all the visible menus left
        if self.choice == None:
            return []
        if len(self.E[self.choice]) == 2:# Menu
            return self.E[self.choice][1].images()# these include the access buttons?

    def undraw(self):
        if self.choice == None:
            return []
        return self.E[self.choice][0].undraw()

    def image(self):# return only the image portion of the self.: I doubt it would be used
        temp = pygame.Surface(self.rect[2:4])
        temp.blit(self.screen, self.rect[0:2])
        return temp

    def getrect(self):
        return (0, YSIZE*20, self.xsize, self.ysize)

