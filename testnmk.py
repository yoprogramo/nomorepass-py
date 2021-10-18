#!/usr/bin/env python

from nomorepass.core import NoMorePass
from datetime import datetime
import qrcode

apikey='FREEAPIKEY' # Change by your own nomorepass apikey

nmp = NoMorePass('api.nomorepass.com',apikey)
now = datetime.now()
timestamp = datetime.timestamp(now)+30 # 30 secs expiry
nmp.setExpiry(timestamp)
qrtext = nmp.getQrNomorekeys ("TestBLEKey","key","12345ABCD","BLEKEY",{'host': 'A0EI3ADYTM', 'extra': {}})
print (qrtext)
img = qrcode.make(qrtext)
img.show()
res = nmp.send()
print(res)
if ('error' in res):
    print ("Error: "+res["error"])
else:
    if ('reason' in res):
        print ("Failed: "+res["reason"])
    else:
        print ("Password received")
        print ("Please, close the qr window")
