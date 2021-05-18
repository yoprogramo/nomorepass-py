#!/usr/bin/env python

from nomorepass.core import NoMorePass
import qrcode

nmp = NoMorePass()
qrtext = nmp.getQrNomorekeys ("Mi Casa","key","897123AF34FAE34","SOUNDKEY",{})
print (qrtext)
img = qrcode.make(qrtext)
img.show()
res = nmp.send()
if ('error' in res):
    print ("Error: "+res["error"])
else:
    print ("Password received")
    print ("Please, close the qr window")
