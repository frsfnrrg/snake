# -*- coding: utf-8 -*-
import os

if __name__ == "__main__":
    from constants import *
else:
    from snakeCode.constants import *

def getNextOpen(seed, indiv):
    # TODO: use a directory content lister, instead of blindly incrementing
    # os.listdir() returns a list of all file names; one could
    # transform that into a list of used numbers
    while os.path.exists(_path(indiv, seed+1)):# the last number has _path called twice
        seed += 1
    return _path(indiv, seed+1)

# usage: r = next(k), r = k.send(tf), r= k.send(tf) ...
def level(number, indiv):
    while True:
        # this yields first, then recieves the next
        # sent value as v
        v = (yield _getattributes( _path(indiv, number), indiv) )

        if v is not None:
            up = v

            if up == True:
                number += 1
                if not os.path.exists(_path(indiv, number)):
                    number = 0
            elif up == False:
                number -= 1
                if number < 0:
                    number += 1
                    while os.path.exists(_path(indiv, number+1)):# the last number has _path called twice
                        number += 1

def _path(indiv, number):
    if indiv:
        return INDIVIDUAL_LEVEL.format(_threedigit(str(number))+".txt")
    else:
        return LEVELSET_MANIFEST.format(_threedigit(str(number)))

def _threedigit(numberstring):
    return "0" * (3 - len(numberstring)) + numberstring

def _getattributes(path, indiv):# open and read that portion of the file
    if indiv:
        return open(path).read().split("\n")[YSIZE+1:YSIZE+3] + [path]
    else:
        return open(path).read().split("\n")[:2] + [path]

def _lgetattributes(path):
    img = pygame.Surface((XSIZE*8,YSIZE*8))
    img.fill((255,255,255))
    if os.path.exists(path[:-4]+"_default.png"):
        img = pygame.transform.smoothscale(pygame.image.load(path[:-4]+"_default.png"), (XSIZE*8,YSIZE*8))
    return [path, img]

def lslevel(ns, number):
    while True:
        v = (yield _lgetattributes( _lpath(ns, number)) )

        if v == True:
            number += 1
            if not os.path.exists(_lpath(ns, number)):
                number = 0
        elif v == False:
            number -= 1
            if number < 0:
                number += 1
                while os.path.exists(_lpath(ns, number+1)):# the last number has _path called twice
                    number += 1

def createnextlevelset():
    n = 0
    while os.path.exists(LEVELSET_MANIFEST.format(_threedigit(str(n)))):
        n += 1
    name = LEVELSET_MANIFEST.format(_threedigit(str(n)))
    os.makedirs(name[:-8],exist_ok=True)
    open(name, "w").write("Unknown\nUnknown\n1")

    return name

def nextopenlpath(start):
    n = 0
    while os.path.exists(start + _threedigit(str(n)) + ".txt"):
        n += 1
    return start + _threedigit(str(n)) + ".txt"
    
def _lpath(ns, number):
   return LEVELSET_LEVEL.format(ns, _threedigit(str(number))+ ".txt") 

def lsi(fpath, inc):
    # fpath is ~~/num/num.txt
    head = fpath[:-7]# ~~/num/
    num = int(fpath[-7:-4])
    print("Current",fpath)
    # for all numbers after num:
    if inc:
        print("increasing")
        num += 1
        rpath = head + _threedigit(str(num)) + ".txt"
    else:
        rpath = fpath
    print("Target",  rpath)

    # scan to head
    nu = 0
    while os.path.exists(head + _threedigit(str(nu)) + ".txt"):
        nu += 1
        
    print(nu)
        
    # cut back
    files = os.listdir(head)
    while nu > num:
        # rename all files beginning with the number
        for fn in filter(lambda l: (len(l)>3 and l[:3] == _threedigit(str(nu - 1))), files):
            new = _threedigit(str(nu)) + fn[3:]
            os.rename(head+fn, head+new)
            print("Renaming",fn, "to", new)

        nu -= 1
    return rpath
   
def emptyfeed():
    img = pygame.Surface((XSIZE*8,YSIZE*8))
    img.fill((255,255,255))
    while True:
        v = (yield ("levels/levelset/000/000.txt", img))
        print(v, "sent to the empty feed.")

if __name__ == "__main__":

    from time import sleep

    for i in level(0, True, True):
        print(i)
        sleep(1)
