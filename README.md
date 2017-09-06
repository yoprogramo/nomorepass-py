# NoMorePass python libraries

## Installation

### Requirements
Install the python-qr libraries

Go to https://github.com/lincolnloop/python-qrcode

Download and execute:

````
sudo python setup.py install
````
The rest of libraries should be included in yout python distribution:

* urllib
* urllib2
* json
* random
* time
* argparse
* base64
* os
* re
* hashlib
* inspect
* sys
* getpass
* Crypto.Cipher.AES

## Examples

### testlocal.py

The local example display a qr-code and waits to scan it with nomorepass app, then it shows by console the data received (using secure nomorepass-protocol2). The window containing the qr is not closed by the program, you should close manually.

### testsend.py

This example generates a unique Qr to send a password securely to a phone (one time use and using protocol2)

````
Send password to app

positional arguments:
  site                 site identification

optional arguments:
  -h, --help           show this help message and exit
  --user USER          username to send
  --password PASSWORD  password to send
````

### test.py
The complete example is designed to work in a Raspberry pi with a TFT screen controlled by ST7735 attached. To install follow this instructions:

1. Install https://github.com/cskau/Python_ST7735 

````
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus python-pip python-imaging python-numpy
````

For a Raspberry Pi make sure you have the RPi.GPIO and Adafruit GPIO libraries by executing:

````
sudo pip install RPi.GPIO
sudo pip install Adafruit_GPIO
````

Install the library by downloading with the download link on the right, unzipping the archive, navigating inside the library's directory and executing:

````
sudo python setup.py install
````

2. Connect Raspberry pi to display (see pinout):

````
TFT   -- RASPBERRY
------------------
LED   -- 3.3v (or other pin to switch on/off screen)
SCK   -- SCLK
SDA   -- MOSI
A0    -- GPIO24
RESET -- GPIO25
CS    -- CE0
GND   -- GND
VCC   -- 3.3v
````

Attach an additional push button between pin GPIO27 (and GND)

Use pin GPIO17 and GPIO18 as output

Run the test

````
python test.py
````

(C) 2017 Jose Antonio Espinosa https://nomorepass.com
