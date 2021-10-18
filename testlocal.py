#!/usr/bin/env python

from nomorepass.core import NoMorePass
from datetime import datetime
import qrcode

apikey='FREEAPIKEY' # Change by your own nomorepass apikey

nmp = NoMorePass('api.nomorepass.com',apikey)
now = datetime.now()
timestamp = datetime.timestamp(now)+30 # 30 secs expiry
nmp.setExpiry(timestamp)
qrtext = nmp.getQrText ('misitio')
print (qrtext)
img = qrcode.make(qrtext)
img.show()
res = nmp.start()
if ('error' in res):
    print ("Error: "+res["error"])
else:
    print ("Usuario: "+res["user"])
    print ("Password: "+res["password"])
    print ("Extra: "+res["extra"])
