#!/usr/bin/env python

from nomorepass.core import NoMorePass
import qrcode

nmp = NoMorePass()
qrtext = nmp.getQrNomorekeys ("Llave Casa Nueva","key","HOLA MUNDO    ","SOUNDKEY",{'extra': {'secret': '1234567890123456'}})
print (qrtext)
img = qrcode.make(qrtext)
img.show()
res = nmp.send()
if ('error' in res):
    print ("Error: "+res["error"])
else:
    print ("Password received")
    print ("Please, close the qr window")
