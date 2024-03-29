# -*- coding: utf-8 -*-
# Copyright (c) 2017, Jose Antonio Espinosa
# All rights reserved.
"""This module implements the protocol 2 of nomorepass.com
"""
import urllib.parse
import urllib.request
import json
import random
import time
from nomorepass import mcrypt as crypt


def nmp_newtoken():
    length = 12
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    retVal = ""
    for i in range (0,length):
        retVal += charset[random.randint(0,len(charset)-1)]
    return retVal

def nmp_decrypt(password,token):
    print("Decoding: ["+password+"] with: "+token)
    dec = crypt.decrypt(token, password)
    return dec

def nmp_encrypt(password,token):
    print("Encoding: ["+password+"] with: "+token)
    dec = crypt.encrypt(token,password,False).decode("utf-8")
    print (dec)
    return dec

class NoMorePass:
    """ Interface to the protocol 2 """
    def __init__(self,server=None,apikey=None):
        if (server==None):
            server='nomorepass.com'
        self.apikey=apikey
        self.server=server
        self.base="https://"+server
        self.getidUrl = self.base+"/api/getid.php"
        self.checkUrl = self.base+"/api/check.php"
        self.referenceUrl = self.base+"/api/reference.php"
        self.grantUrl = self.base+"/api/grant.php"
        self.pingUrl = self.base+"/api/ping.php"
        self.stopped = False
        self.expiry = None

    def getQrText (self,site):
        params = {'site': site}
        if self.expiry!=None:
            params['expiry'] = self.expiry
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(self.getidUrl,data)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
        if (self.apikey!=None):
            req.add_header('apikey',self.apikey)
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            data = r.read()
            decoded = json.loads(data)
            if (decoded["resultado"]=="ok"):
                self.ticket = decoded["ticket"]
                self.token = nmp_newtoken()
                text = 'nomorepass://'+self.token+self.ticket+site
                return text
            else:
                return False
    
    def getQrNomorekeys (self,site, user, password, type, extra):
        """ Returns the QR url to send a nomorekeys key to the phone """
        """ basically the same as getQRSend but with nomorekeys://   """
        """ only available for soundkey and lightkey right now       """
        """ SOUNDKEY passwords are limited to 14 characters          """
        if type!="SOUNDKEY" and type!="LIGHTKEY" and type!="BLEKEY":
            type="KEY" # clave genérica por defecto
        if (site==None):
            site='WEBDEVICE'
        device = 'WEBDEVICE'
        param = urllib.parse.urlencode({'device': device,'fromdevice':device}).encode("utf-8")
        req = urllib.request.Request(self.referenceUrl,param)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
        if (self.apikey!=None):
            req.add_header('apikey',self.apikey)
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            body = r.read()
            response = json.loads(body)
            print (body)
            if (response["resultado"]=="ok"):
                token = response["token"]
                params = {'site': site}
                if self.expiry!=None:
                    params['expiry'] = self.expiry
                param = urllib.parse.urlencode(params).encode("utf-8")
                req = urllib.request.Request(self.getidUrl,param)
                req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
                if (self.apikey!=None):
                    req.add_header('apikey',self.apikey)
                r = urllib.request.urlopen(req)
                if (r.getcode()==200):
                    body = r.read()
                    response = json.loads(body)
                    if (response["resultado"]=="ok"):
                        tk = nmp_newtoken()
                        self.token = tk
                        self.ticket = response["ticket"]
                        if (type=='SOUNDKEY'):
                            password = password[:14].ljust(14)
                        else:
                            if type=='LIGHTKEY':
                                #lightkeys son un solo entero, la clave ha de ser
                                #un numero de 0 a 65536 (unsigned) por lo que
                                #hacemos el resto y volvemos a pasar a cadena
                                password = str(int(password)%65536)

                        ep = nmp_encrypt(password,tk)
                        if (isinstance(extra,dict)):
                            if 'extra' in extra.keys():
                                if isinstance(extra['extra'],dict) and 'secret' in extra['extra'].keys():
                                    extra['extra']['secret']=nmp_encrypt(str(extra['extra']['secret']),tk)
                                else:
                                    if not isinstance(extra['extra'],dict):
                                        extra['extra'] = {'type': type.lower()}
                            if 'type' not in extra['extra'].keys():
                                extra['extra']['type'] = type.lower()
                            extra['type'] = type.lower();
                            extra = json.dumps(extra)
                        else:
                            extra = {'type':type.lower(), 'extra': {'type': type.lower()}}
                            if type=='KEY':
                                extra['extra']['type'] = 'padkey'
                            extra = json.dumps(extra)
                        param = urllib.parse.urlencode({'grant': 'grant','ticket':self.ticket,'user':user,'password':ep,'extra':extra}).encode("utf-8")
                        req = urllib.request.Request(self.grantUrl,param)
                        req.add_header('User-Agent', 'NoMoreKeys-IoT/1.0')
                        if (self.apikey!=None):
                            req.add_header('apikey',self.apikey)
                        r = urllib.request.urlopen(req)
                        if (r.getcode()==200):
                            body = r.read()
                            response = json.loads(body)
                            print("Granted")
                            text = 'nomorekeys://'+type+tk+response['ticket']+site
                            return text
                        else:
                            print("Error calling grant")
                            return False
                    else:
                        print("Not known device")
                        return False
                else:
                    print("Error calling getid")
                    return False
            else:
                print("Unknown device")
                return False
        else:
            print("Error calling reference")
            return False

    def start(self):
        #Comenzamos a preguntar (check) si nos han enviado el pass
        #dado que esta función es síncrona no devolvemos el control
        #hasta que tenemos una respuesta (positiva o negativa)
        #o hasta que el valor del atributo stopped es cierto

        while (self.stopped == False):
            data = urllib.parse.urlencode({'ticket': self.ticket}).encode("utf-8")
            req = urllib.request.Request(self.checkUrl,data)
            req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
            if (self.apikey!=None):
                req.add_header('apikey',self.apikey)
            r = urllib.request.urlopen(req)
            if (r.getcode()==200):
                data = r.read()
                decoded = json.loads(data)
                if (decoded["resultado"]=="ok"):
                    if (decoded["grant"]=='deny'):
                        return {'error': 'denied'}
                    else:
                        if (decoded["grant"]=='grant'):
                            data = {'user': decoded["usuario"],'password': nmp_decrypt(decoded["password"],self.token),'extra' : decoded.get('extra','')}
                            return data
                        else:
                            if (decoded["grant"]=='expired'):
                                return {'error': 'expired'}
                            else:
                                #Esperamos un poco y volvemos a llamarnos
                                time.sleep(4)
                                #continuamos el bucle
                else:
                    return {'error': 'network error'}
            else:
                return {'error': 'network error'}
        else:
            self.stopped = False
        return {'error': 'stopped'}

    def stop(self):
        self.stopped = True

    def getQrSend (self,site, user, password, extra):
        if (site==None):
            site='WEBDEVICE'
        device = 'WEBDEVICE'
        param = urllib.parse.urlencode({'device': device,'fromdevice':device}).encode("utf-8")
        req = urllib.request.Request(self.referenceUrl,param)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
        if (self.apikey!=None):
            req.add_header('apikey',self.apikey)
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            body = r.read()
            response = json.loads(body)
            print (body)
            if (response["resultado"]=="ok"):
                token = response["token"]
                params = {'site': site}
                if self.expiry!=None:
                    params['expiry'] = self.expiry
                param = urllib.parse.urlencode(params).encode("utf-8")
                req = urllib.request.Request(self.getidUrl,param)
                req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
                if (self.apikey!=None):
                    req.add_header('apikey',self.apikey)
                r = urllib.request.urlopen(req)
                if (r.getcode()==200):
                    body = r.read()
                    response = json.loads(body)
                    if (response["resultado"]=="ok"):
                        tk = nmp_newtoken()
                        self.token = tk
                        self.ticket = response["ticket"]
                        ep = nmp_encrypt(password,tk)
                        if (isinstance(extra,dict)):
                            if 'extra' in extra.keys():
                                if isinstance(extra['extra'],dict) and 'secret' in extra['extra'].keys():
                                    extra['extra']['secret']=nmp_encrypt(str(extra['extra']['secret']),tk)
                            extra = json.dumps(extra)
                        param = urllib.parse.urlencode({'grant': 'grant','ticket':self.ticket,'user':user,'password':ep,'extra':extra}).encode("utf-8")
                        req = urllib.request.Request(self.grantUrl,param)
                        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
                        if (self.apikey!=None):
                            req.add_header('apikey',self.apikey)
                        r = urllib.request.urlopen(req)
                        if (r.getcode()==200):
                            body = r.read()
                            response = json.loads(body)
                            print("Granted")
                            text = 'nomorepass://SENDPASS'+tk+response['ticket']+site
                            return text
                        else:
                            print("Error calling grant")
                            return False
                    else:
                        print("Not known device")
                        return False
                else:
                    print("Error calling getid")
                    return False
            else:
                print("Unknown device")
                return False
        else:
            print("Error calling reference")
            return False

    def send (self):
        while True:
            param = urllib.parse.urlencode({'device': 'WEBDEVICE', 'ticket': self.ticket}).encode("utf-8")
            req = urllib.request.Request(self.pingUrl,param)
            req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
            if (self.apikey!=None):
                req.add_header('apikey',self.apikey)
            r = urllib.request.urlopen(req)
            if (r.getcode()==200):
                body = r.read()
                response = json.loads(body)
                if (response["resultado"]=="ok" and response["ping"]=="ok"):
                    time.sleep(4)
                else:
                    return response
    
    def sendRemotePassToDevice (self,cloud,deviceid,secret,username,password):
        # Envía una contraseña remota a un dispositivo cloud
        # cloud: url de /extern/send_ticket 
        # devideid: id del dispositivo
        # secret: md5 del secreto del dispositivo
        # username: usuario
        # password: contraseña
        cloudurl = cloud
        if cloudurl==None:
            cloudurl = "https://api.nmkeys.com/extern/send_ticket"
        token = secret
        params = {'site': 'Send remote pass'}
        if self.expiry!=None:
            params['expiry'] = self.expiry
        param = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(self.getidUrl,param)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
        if (self.apikey!=None):
            req.add_header('apikey',self.apikey)
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            body = r.read()
            response = json.loads(body)
            if response["resultado"]=="ok":
                ticket = response["ticket"]
                ep = nmp_encrypt(password,token)
                param = urllib.parse.urlencode({'grant': 'grant', 'ticket': ticket, 'user': username, 'password': ep, 'extra': '{"type": "remote"}'}).encode("utf-8")
                req = urllib.request.Request(self.grantUrl,param)
                req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
                if (self.apikey!=None):
                    req.add_header('apikey',self.apikey)
                r = urllib.request.urlopen(req)
                if (r.getcode()==200):
                    body = r.read()
                    response = json.loads(body)
                    if response["resultado"]=="ok":
                        param = json.dumps({'hash': token[:10], 'ticket': ticket, 'deviceid': deviceid}).encode("utf-8")
                        req = urllib.request.Request(cloudurl,data=param,headers={'content-type': 'application/json'})
                        r = urllib.request.urlopen(req)
                        if (r.getcode()==200):
                            body = r.read()
                            response = json.loads(body)
                            return response
                        else:
                            return "error calling "+cloudurl
                    else:
                        print ("Error en granturl")
                        return response
                else:
                    return "error calling granturl"
            else:
                return response
        else:
            return "error calling getid"

    def setExpiry(self, expiry):
        self.expiry = expiry
        
