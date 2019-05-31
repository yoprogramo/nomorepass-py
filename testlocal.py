#!/usr/bin/env python

from nomorepass.core import NoMorePass
import qrcode

nmp = NoMorePass()
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
