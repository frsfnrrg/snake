# -*- coding: utf-8 -*-
import os


# self.H form is
# if each branch s.h[0],s.h[1]
# there is an array of [ [number], [speed, record], [speed, record]      ]
# the arrays are sorted from greatest number to least number
# the pairs are sorted from fastest to slowest

class highscores():

    def __init__(self):
        # LEVELNUMBER; speed,moves; speed,moves;
        # I think the below is too slow-could have just a single while loop with ifs in it. Splits are unweildy
        self.scorenames = ["highscores_individual.txt","highscores_levelset.txt"]
        self.H = [[],[]]
        for i in range(2):
            if os.path.exists(self.scorenames[i]):# Load the highscores.txt in HIGHSCORES
                self.H[i] = open(self.scorenames[i], "r").read().split("\n")
                for l in range(len(self.H[i])):
                    self.H[i][l] = self.H[i][l].split(";")
                    for k in range(len(self.H[i][l])):
                        self.H[i][l][k] = self.H[i][l][k].split(",")
                        for m in range(len(self.H[i][l][k])):
                            self.H[i][l][k][m] = int(self.H[i][l][k][m])
            else:
                print(self.scorenames[i].title() + " does not exist. It will be created when a record is set.")

    # for clarity and conciseness :-)
    def updateIndividual(self, maxSpeed, fieldnum, moveCount):# TODO redesign process
        found = -1
        Record = None
        k = 0
        for k in range(len(self.H[0])):
            if fieldnum == self.H[0][k][0][0]:
                found = k
        if found == -1:# If no highscore exists for this level:
            z = 0
            while z < len(self.H[0]) and self.H[0][z][0][0] > fieldnum:
                z += 1
            self.H[0].insert(z, [[fieldnum], [maxSpeed,moveCount]])
            Record = moveCount
        else: # If a highscore exists - this is problematic sometimes
            y = 0
            while y < len(self.H[0][found])-1 and self.H[0][found][y+1][0] >= maxSpeed:
                y += 1

            # find if one is there at the correct speed
            if self.H[0][found][y][0] == maxSpeed:
                if self.H[0][found][y][1] < moveCount:# get the record
                    Record = self.H[0][found][y][1]
                else:
                    Record = self.H[0][found][y][1] = moveCount# or improve it
            else:
                Record = moveCount# set it and insert it for that speed
                self.H[0][found].insert(y+1, [maxSpeed,moveCount])# place it in th

        self.write(0)
        return Record

    def getrecord(self, gametype, levelnumber, speed):
        for i in self.H[gametype]:
            if i[0][0] == levelnumber:
                for j in i[1:-1]:
                    if j[0] == speed:
                        return j[1]

        return None

    def updateLevelset(self, maxSpeed, levelsetnum, levelreached, cheat):
        found = -1
        Record = None
        k = 0
        for k in range(len(self.H[1])):
            if levelsetnum == self.H[1][k][0][0]:
                found = k
        if found == -1:# If no highscore exists for this level:
            z = 0
            while z < k and self.H[1][z+1][0][0] > levelsetnum:
                z += 1
            self.H[1].insert(z, [[levelsetnum], [maxSpeed,levelreached]])
            Record = levelreached
        else: # If a highscore exists - this is problematic sometimes
            y = 0
            while y < len(self.H[1][found])-1 and self.H[1][found][y+1][0] >= maxSpeed:
                y += 1

            # find if one is there at the correct speed
            if self.H[1][found][y][0] == maxSpeed:
                if self.H[1][found][y][1] > levelreached:# get the record
                    Record = self.H[1][found][y][1]
                else:
                    Record = self.H[1][found][y][1] = levelreached# or improve it
            else:
                Record = levelreached
                self.H[1][found].insert(y+1, [maxSpeed,levelreached])# place it in the right order?

        if cheat == True:# it will never be written
            return Record
        self.write(1)
        return Record

    def write(self, gametype):
        text = ""
        for l in range(len(self.H[gametype])):
            text += str(self.H[gametype][l][0][0])
            for s in range(1,len(self.H[gametype][l])):
                text += ";" + str(self.H[gametype][l][s][0]) + "," + str(self.H[gametype][l][s][1])
            if l != len(self.H[gametype])-1:
                text += "\n"

        open(self.scorenames[gametype],"w").write(text)
