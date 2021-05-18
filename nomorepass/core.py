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
    dec = crypt.decrypt(password, token)
    return dec

def nmp_encrypt(password,token):
    print("Encoding: ["+password+"] with: "+token)
    dec = crypt.encrypt(token,password,False)
    print (dec)
    return dec

class NoMorePass:
    """ Interface to the protocol 2 """
    def __init__(self,server=None):
        if (server==None):
            server='nomorepass.com'
        self.server=server
        self.base="https://"+server
        self.getidUrl = self.base+"/api/getid.php"
        self.checkUrl = self.base+"/api/check.php"
        self.referenceUrl = self.base+"/api/reference.php"
        self.grantUrl = self.base+"/api/grant.php"
        self.pingUrl = self.base+"/api/ping.php"
        self.stopped = False

    def getQrText (self,site):
        data = urllib.parse.urlencode({'site': site}).encode("utf-8")
        req = urllib.request.Request(self.getidUrl,data)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
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
        if type!="SOUNDKEY" and type!="LIGHTKEY":
            return False
        if (site==None):
            site='WEBDEVICE'
        device = 'WEBDEVICE'
        param = urllib.parse.urlencode({'device': device,'fromdevice':device}).encode("utf-8")
        req = urllib.request.Request(self.referenceUrl,param)
        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            body = r.read()
            response = json.loads(body)
            print (body)
            if (response["resultado"]=="ok"):
                token = response["token"]
                param = urllib.parse.urlencode({'site': site}).encode("utf-8")
                req = urllib.request.Request(self.getidUrl,param)
                req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
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
                            extra['extra'] = {'type': type.lower()}
                            extra = json.dumps(extra)
                        else:
                            extra = {'extra': {'type': type.lower()}}
                            extra = json.dumps(extra)
                        param = urllib.parse.urlencode({'grant': 'grant','ticket':self.ticket,'user':user,'password':ep,'extra':extra}).encode("utf-8")
                        req = urllib.request.Request(self.grantUrl,param)
                        req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
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
        r = urllib.request.urlopen(req)
        if (r.getcode()==200):
            body = r.read()
            response = json.loads(body)
            print (body)
            if (response["resultado"]=="ok"):
                token = response["token"]
                param = urllib.parse.urlencode({'site': site}).encode("utf-8")
                req = urllib.request.Request(self.getidUrl,param)
                req.add_header('User-Agent', 'NoMorePass-IoT/1.0')
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
            r = urllib.request.urlopen(req)
            if (r.getcode()==200):
                body = r.read()
                response = json.loads(body)
                if (response["resultado"]=="ok" and response["ping"]=="ok"):
                    time.sleep(4)
                else:
                    return response

