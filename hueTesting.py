#!/usr/bin/env python

from os import path
from qhue import Bridge, QhueException, create_new_username
from time import time
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

class LightController:

    def __init__(self, lightBinding, br = BRI_MAX/2, hu = RED, sa = SAT_MAX/2):
        self.br = br
        self.hu = hu
        self.sa = sa
        self.light = lightBinding

    def setBHS(self, br=BRI_MAX/2, sa=SAT_MAX/2, hu = RED):
        self.light.state(bri = br, hue = hu, sat=sa)
        self.hu = hu
        self.br = br
        self.sa = sa

    def setBrightness(self, br):
        self.light.state(bri = br)
        self.br = br

    def setHue(self, hu):
        self.light.state(hue = hu)
        self.hu = hu

    def setSat(self, sa):
        self.light.state(sat = sa)
        self.sa = sa

    def fadeOut(self, decayTime):
        #TODO : rewrite using transitiontime
        br0 = self.br
        decByHalfSec = br0 / (decayTime * 2)
        t0 = time()
        while br0 > 0:
            currT = time()
            if t0 - currT > 0.5:
                br0 -= decByHalfSec
                self.setBrightness(br0)
                t0 = currT
  
    def fadeIn(self, decayTime, toBri = 128):
        #TODO : rewrite using transitiontime
        br0 = self.br
        if br0 > 10 or br0 < 0:
            return
        else :
            decByHalfSec = (toBri - br0) / (decayTime * 2)
            t0 = time()
            while br0 < toBri:
                currT = time()
                if t0 - currT > 0.5:
                    br0 += decByHalfSec
                    self.setBrightness(br0)
                    t0 = currT


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

    #rainbow(lights[2])
    #peterLAmpoule(lights[2])
    #traficLight(lights[2])
    #rainbow(lights[2])
    #traficLight2(light[1], light[2])
    #peterLAmpoule(light)
    rainbow(light)
    #light[1].state(bri=0, hue=RED, transitiontime=0)
    #light[2].state(bri=0, hue=RED, transitiontime=0)

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
    lastSec = time()
    while True:
        if i > 254:
            i = 50

        if hu > 65535:
            hu = 0

        currT = time()
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


def traficLight2(light1, light2, defBri = 254):
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
