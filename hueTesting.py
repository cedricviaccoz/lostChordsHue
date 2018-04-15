#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException, create_new_username
import time
import random
import re

# the path for the username credentials file
CRED_FILE_PATH = "qhue_username.txt"

#Max values that parameters of the lightbulb can take
HUE_MAX = 2**16 - 2
SAT_MAX = 2**8 - 2
BRI_MAX = 2**8 - 2

GREEN = 21845
RED = 0
ORANGE = 5460
PRETTY_ORANGE = 2**12
BLUE = 43600
FUCHSIA = 56420
LEMON = 10550
SLIMEGREEN = 31850
TURQUOISE = 35000
MAUVE = 47350
#PURPLE : H = 279/360 S = 94% B = 82%
PURPLE = 50790

QUART_REG = '(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
IP_REG = QUART_REG+'.'
IP_REG += QUART_REG+'.'
IP_REG += QUART_REG+'.'
IP_REG += QUART_REG

COLORS = [RED, GREEN, BLUE]

phase1 = [
    ["001", 0.25],
    ["010", 0.5],
    ["011", 0.6],
    ["100", 0.85],
    ["101", 0.9],
    ["110", 1] 
]

phase2 = [
    ["001", 0.15],
    ["010", 0.3],
    ["011", 0.5],
    ["100", 0.65],
    ["101", 0.8],
    ["110", 1] 
]

phase3 = [
    ["001", 0.05],
    ["010", 0.1],
    ["011", 0.3],
    ["100", 0.35],
    ["101", 0.55],
    ["110", 0.75],
    ["111", 1] 
]

def main():

    # check for a credential file
    if not path.exists(CRED_FILE_PATH):

        print('Please enter the IP adress of the bridge')
        regex = re.compile(IP_REG, flags=re.IGNORECASE)
        BRIDGE_IP = input('> ')

        while not regex.match(BRIDGE_IP):
            print('You did not enter a valid IP adress, please try again')
            BRIDGE_IP = input('> ')

        while True:
            try:
                username = create_new_username(BRIDGE_IP)
                break
            except QhueException as err:
                print("Error occurred while creating a new username: {}".format(err))

        # store the username in a credential file
        with open(CRED_FILE_PATH, "w") as cred_file:
            cred_file.write(username+'\n')
            cred_file.write(BRIDGE_IP)

    else:
        with open(CRED_FILE_PATH, "r") as cred_file:
            lines = cred_file.read().split('\n')
            username = lines[0]
            BRIDGE_IP = lines[1]

    # create the bridge resource, passing the captured username
    bridge = Bridge(BRIDGE_IP, username)

    # create a lights resource
    light = bridge.lights
    scheduler(light)
    #SecSwitchAndFadeIn(light[1])

def getPhase(ti):
    if ti > 480:
        return phase3
    elif ti > 240:
        return phase2
    else:
        return phase1

def extractNextComb(phase):
    prevProb = 0
    sel = random.random()
    for row in phase:
        currProb = row[1]
        if sel > prevProb and sel <= currProb:
            m = map(lambda c : True if c == '0' else False, list(row[0]))
            lhlh = []
            for l in m:
                lhlh.append(l)
            return lhlh
        prevProb = currProb

def switchLights(currComb, lights):
    ind = 0
    while(ind < 3):
        if currComb[ind]:
            lights[ind].state(bri = 200)
        ind += 1
    t0 = time.clock()
    t1 = time.clock()
    while(t0 - t1 < 4):
        t1 = time.clock()
    ind = 0
    while(ind<3):
        if not currComb[ind]:
            lights[ind].state(bri = 0)
        ind += 1


def switchLights2(currComb, lights):
    if currComb[0]:
        lights[1].state(bri = 250)
    if currComb[1] and currComb[2]:
        lights[2].state(bri = 250, hue = PURPLE)
    elif currComb[1]:
        lights[2].state(bri = 250, hue = BLUE)
    elif currComb[2]:
        lights[2].state(bri = 250, hue = RED)
    else:
        lights[2].state(bri = 0)
    if not currComb[0]:
        lights[1].state(bri=0)

def scheduler(lights):
        #fadein/fadeout of 4 seconds
    lights[1].state(bri = 0, hue = GREEN, transitiontime = 80, sat = SAT_MAX)
    lights[2].state(bri = 0, hue = BLUE, transitiontime = 80, sat = SAT_MAX)
    #lights[2].state(bri = 0, hue = RED,  transitiontime = int(4000))
    t0 = time.time()
    tPrevious = t0
    tCurr = t0
    while(tCurr - t0 < 700.0): #720 seconds is 12 minutes
        phase = getPhase(t0-tCurr)
        if tCurr - tPrevious> 20.0:
            tPrevious = tCurr
            currComb = extractNextComb(phase)
            for p in currComb:
                print(p)
            switchLights2(currComb, lights)
        tCurr = time.time()

    lights[1].state(bri = 250, hue=GREEN)
    lights[2].state(bri = 250, hue=PURPLE)
    while(t0 - tCurr < 740):
        tCurr = time.time()
    lights[1].state(bri = 0, hue=GREEN)
    lights[2].state(bri = 0, hue=PURPLE)


def peterLAmpoule(light):
    br = 0
    lastSec = time()
    while True:
        currT = time()
        if currT - lastSec > 0.01:
            lastSec = currT
            br += 1
            light[1].state(bri=(br % 2)*254, hue=RED, transitiontime=0)
            light[2].state(bri=(br % 2)*254, hue=RED, transitiontime=0)


def SecSwitchAndFadeIn(light):
    i = 50
    hu = 0
    lastSec = time.time()
    while True:
        if i > 254:
            i = 50

        if hu > 65535:
            hu = 0

        currT = time.time()
        if currT - lastSec > 1:
            lastSec = currT
            hu += 1
            light.state(bri=i % 255, hue=COLORS[i % 3])
            i += 10

def strobo(light, defHue=0):
    br = 0
    lastSec = time()
    while True:
        currT = time()
        if currT - lastSec > 0.75:
            lastSec = currT
            light.state(bri=(br % 2)*254, hue=defHue)
            br += 1


def traficLight(light, defBri = 254):
    hu = 0
    lastSec = time()
    while True:
        currT = time()
        if currT - lastSec > 0.25:
            lastSec = currT
            light.state(bri=defBri, hue=COLORS[hu%2], transitiontime=0)
            hu += 1


def christmasTime(light1, light2, defBri = 254):
    hu = 0
    lastSec = time()
    while True:
        currT = time()
        if currT - lastSec > 0.75:
            lastSec = currT
            light1.state(bri=defBri, hue=COLORS[hu%2], transitiontime=0)
            light2.state(bri=defBri, hue=COLORS[(hu+1)%2], transitiontime=0)
            hu += 1


def rainbow(light, defBri = 254):
    hu = 0
    lastSec = time()
    while True:
        currT = time()
        if currT - lastSec > 1.2:
            lastSec = currT
            light[2].state(bri=defBri, hue=hu%65535, sat=SAT_MAX, transitiontime=100)
            light[1].state(bri=defBri, hue=hu%65535, sat=SAT_MAX, transitiontime=100)
            hu += 2**12
            if hu >65000:
                hu = 0

if __name__ == "__main__":
    main()
