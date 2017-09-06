# Copyright (c) 2017 BiblioEteca Technologies
# Author: Jose Antonio Espinosa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from PIL import Image

import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import qrcode
from nomorepass.core import NoMorePass
from uuid import getnode as get_mac
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)
GPIO.output(17,True)

isopen = False
opencnt = 0

mac = get_mac()
macaddr = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000


# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

# BeagleBone Black configuration.
# DC = 'P9_15'
# RST = 'P9_12'
# SPI_PORT = 1
# SPI_DEVICE = 0

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display.
disp.begin()
image = Image.open ('logo.png')
disp.display(image)

print ("Esperando pulsacion")

def openDoor ():
    print "Opening..."
    GPIO.output(18,False)
    GPIO.output(17,True)
    isopen = True
    opencnt = 40

def closeDoor():
    print "Clossing..."
    GPIO.output(17,False)
    GPIO.output(18,True)
    isopen = False
    opencnt = 0

def showqr():
    nmp = NoMorePass()
    qrtext = nmp.getQrText ("iot"+macaddr)

    # Load an image.
    print('Generating qr...')
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qrtext)
    qr.make(fit=True)

    image = qr.make_image()
    #image = Image.open('qr.png')
    background = Image.new('RGBA', (WIDTH,HEIGHT), (255, 255, 255, 255))

    # Resize the image and rotate it so matches the display.
    image = image.rotate(90).resize((WIDTH, WIDTH))
    offset = (0, 16)
    background.paste (image,offset)

    # Draw the image on the display hardware.
    print('Drawing image')
    disp.display(background)

    res = nmp.start()
    if ('error' in res):
        print "Error: "+res["error"]
    else:
        usuario = res["user"]
        password = res["password"]
        extra =  res["extra"]
        if (usuario=='test' and password=='test1'):
            image = Image.open ('logo.png')
            openDoor()
        else:
            image = Image.open ('logo-no.png')
            closeDoor()
        disp.display(image)


while True:
    input_state = GPIO.input(27)
    if (opencnt>0):
        opencnt=opencnt-1
    if (opencnt==0):
        closeDoor()
        opencnt = -1;
    if (input_state == False):
        print ("Pulsado")
        showqr()
    time.sleep(0.2)
