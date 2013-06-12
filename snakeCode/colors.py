# -*- coding: utf-8 -*-
from math import sqrt

colors = "MONKEY"

class GUIColors():

    # 'Header' & Menus
    header =        (127,127,143)# slightly greenish gray
    headerrim =     (63, 63, 71 )# darker greenish gray
    textboxbg =     (119,119,135)# an in-between shade

    # Messages
    messagebg =     (201,201,201,200)
    record =        (200,160,40 )# pastel yellow
    win =           (50, 20, 30 )# A deep, rich, luxurious purple: bask in its glory!
    collide =       (20, 30, 50 )# blue/slate
    begin =         (30, 50, 20 )# green
    paused =        (20, 50, 50 )# blue-green
    gameover =      (20, 20, 20 )# near black

    # Buttons!

    button =        (100,100,100)# medium gray
    buttonclick =   (70, 70, 70 )# darker gray

    quit =          (100,0,  0  )# dark red
    pause =         (0,  0,  100)# dark blue
    new =           (0,  100,0  )# dark green
    help =          (255,255,255)# white
    options =       (5,  5,  5  )# near black
    save =          (0,  100,100)# dark blue-green

    # Numbers
    plusminus =     (50, 50, 50 )# dark gray
    numbers =       (40, 40, 30 )# yellowish gray: too bland
    # COunters
    moves =         (0,  0,  75 )# Dark Green
    lives =         (75, 0,  0  )# Dark Red

    # MENU OPTIONS
    fast =          (220,50, 50 )# Red
    speedy =        (220,120,50 )# Orange
    relaxed =       (50, 175,50 )# Green
    slow =          (200,50, 200)# Purple

    default =       (0,  55, 0  )# Green
    inverted =      (255,175,175)# Pink
    graybutton =    (20, 20, 20 )# dark gray/grey
    worm =          (150,100,0  )# brown

    levelset =      (10, 50, 50 )# Blue-Green
    individual =    (10, 10, 10 )# Near Black

    levelselect =   (255,255,255)# White

    # AUX.
    namebox =       (0,  75, 0  )# dark blue!

    lsbg =          (0,  0,  0  )# black


COLORLIST = ["default", "inverted", "gray", "worm"]

class LevelColors():

    def __init__(self):
        pass

    def Default(self):
        self.CS = "default"
        # FIELD COLORS: CHANGEABLE
        self.snake =            (0,  191,0  )# bright green
        self.snakejoint =       (0,  95, 0  )# dark green
        self.wall =             (50, 50, 50 )# gray
        self.wallconnect =      (36, 36, 36 )# dark gray
        self.bg =               (3,  3,  3  )# almost black
        self.banana =           (223,223,63 )# bright yellow
        self.goal =             (63, 191,255)# bright cyan

    def Inverted(self):
        self.CS = "inverted"
        self.snake =            (255,169,255)
        self.snakejoint =       (255,200,255)
        self.wall =             (200,200,200)
        self.wallconnect =      (210,210,210)
        self.bg =               (254,254,254)
        self.banana =           (123,123,247)
        self.goal =             (247,169,6  )

    def Gray(self):
        self.CS = "gray"
        self.snake =            (0,  0,  0  )# black
        self.snakejoint =       (50, 50, 50 )# near black
        self.wall =             (0,  0,  0  )# black
        self.wallconnect =      (50, 50, 50 )# near black
        self.bg =               (255,255,255)# white
        self.banana =           (175,175,175)# bright
        self.goal =             (100,100,100)# dark

    def Worm(self):# brown dirt, pink/brown worm, green food, black goal
        self.CS = "worm"
        self.snake =            (117,77, 38 )
        self.snakejoint =       (160,107,53 )
        self.wall =             (97, 64, 0  )
        self.wallconnect =      (128,85, 0  )
        self.bg =               (77, 51, 0  )
        self.banana =           (15, 125,15 )
        self.goal =             (0,  0,  0  )

    def setColorScheme(self, colorscheme):
        if colorscheme == "inverted":
            self.Inverted()
        elif colorscheme == "default":
            self.Default()
        elif colorscheme == "gray":# darn you bloody whippersnappers
            self.Gray()
        elif colorscheme == "worm":
            self.Worm()
        else:
            raise Doomsicle("Nasty chuckle")

    def getColorScheme(self):
        return self.CS