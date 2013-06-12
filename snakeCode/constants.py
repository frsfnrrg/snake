# -*- coding: utf-8 -*-
# These are invariant!
import pygame
pygame.font.init()
# Buttons
BUTTON_HEIGHT = 36
TOOLBUTTON_SIZE = 54
# DEFAULT
_fontpath = None
SMALL_FONT = pygame.font.Font(_fontpath, 24)
MEDIUM_FONT = pygame.font.Font(_fontpath, 40)
BIG_FONT = pygame.font.Font(_fontpath, 60)

class Doomsicle(BaseException):
    pass

#Font size of 10000 - 6876H
# GAME ASPECTS
XSIZE = 50
YSIZE = 30
SNAKE_LIVES = 5
# Button Codes
PLAIN_BUTTON = 0
PASSIVE_BUTTON = 1
LOCK_BUTTON = 2
ITEM_BUTTON = 3
# TEXTBOX CODES
EXTENDABLE_TEXTBOX = True
FIXED_TEXTBOX = False
#File Addresses - used for formal
INDIVIDUAL_LEVEL = "levels/individual/{}"
LEVELSET_LEVEL = "levels/levelset/{}/{}"
LEVELSET_MANIFEST = "levels/levelset/{}/Info.txt" 
#
LETTERDICT = {
    (9,False):      "    ",
    (9,True):       "    ",


    (32,False):     " ",
    (32,True):      " ",

    (39,False):     "\'",
    (39,True):      "\"",

    (44,False):     ",",
    (44,True):      "<",
    (45,False):     "-",
    (45,True):      "_",
    (46,False):     ".",
    (46,True):      ">",
    (47,False):     "/",
    (47,True):      "?",


    (48,False):     "0",
    (49,False):     "1",
    (50,False):     "2",
    (51,False):     "3",
    (52,False):     "4",
    (53,False):     "5",
    (54,False):     "6",
    (55,False):     "7",
    (56,False):     "8",
    (57,False):     "9",

    (48,True):      ")",
    (49,True):      "!",
    (50,True):      "@",
    (51,True):      "#",
    (52,True):      "$",
    (53,True):      "%",
    (54,True):      "^",
    (55,True):      "&",
    (56,True):      "*",
    (57,True):      "(",

    (59,False):     ";",
    (59,True):      ":",

    (61,False):     "=",
    (61,True):      "+",

    (91,False):     "[",
    (91,True):      "{",
    (92,False):     "\\",
    (93,True):      "|",
    (93,False):     "]",
    (93,True):      "}",


    (96,False):     "`",
    (96,True):      "~",

    (97,False):     "a",
    (98,False):     "b",
    (99,False):     "c",
    (100,False):    "d",
    (101,False):    "e",
    (102,False):    "f",
    (103,False):    "g",
    (104,False):    "h",
    (105,False):    "i",
    (106,False):    "j",
    (107,False):    "k",
    (108,False):    "l",
    (109,False):    "m",
    (110,False):    "n",
    (111,False):    "o",
    (112,False):    "p",
    (113,False):    "q",
    (114,False):    "r",
    (115,False):    "s",
    (116,False):    "t",
    (117,False):    "u",
    (118,False):    "v",
    (119,False):    "w",
    (120,False):    "x",
    (121,False):    "y",
    (122,False):    "z",
    (97,True):      "A",
    (98,True):      "B",
    (99,True):      "C",
    (100,True):     "D",
    (101,True):     "E",
    (102,True):     "F",
    (103,True):     "G",
    (104,True):     "H",
    (105,True):     "I",
    (106,True):     "J",
    (107,True):     "K",
    (108,True):     "L",
    (109,True):     "M",
    (110,True):     "N",
    (111,True):     "O",
    (112,True):     "P",
    (113,True):     "Q",
    (114,True):     "R",
    (115,True):     "S",
    (116,True):     "T",
    (117,True):     "U",
    (118,True):     "V",
    (119,True):     "W",
    (120,True):     "X",
    (121,True):     "Y",
    (122,True):     "Z",
}
    #[(event.key,self.shift)]