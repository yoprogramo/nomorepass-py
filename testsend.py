#!/usr/bin/env python

from nomorepass.core import NoMorePass
import qrcode
import argparse

parser = argparse.ArgumentParser(description='Send password to app')
parser.add_argument('--user', help='username to send')
parser.add_argument('--password', help='password to send')
parser.add_argument('site', help='site identification')

args = parser.parse_args()
user = args.user
password = args.password
site = args.site

nmp = NoMorePass()
qrtext = nmp.getQrSend(site,user,password,{'type':'pwd'})
img = qrcode.make(qrtext)
img.show()
res = nmp.send()
if ('error' in res):
    print "Error: "+res["error"]
else:
    print "Password received"
    print "Please, close the qr window"
   
