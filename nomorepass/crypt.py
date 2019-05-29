from os import urandom
from hashlib import md5
import base64

from Crypto.Cipher import AES

def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = b''  # changed '' to b''
    while len(d) < key_length + iv_length:
        # changed password to str.encode(password)
        d_i = md5(d_i + str.encode(password) + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(in_str, password, salt_header='Salted__', key_length=32):
    bs = AES.block_size
    salt = urandom(bs - len(salt_header))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    result = b''
    result += str.encode(salt_header)+salt
    finished = False
    offset = 0
    while not finished:
        chunk = str.encode(in_str[offset:offset+(1024*bs)])
        offset += (1024*bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += str.encode(
                padding_length * chr(padding_length))
            finished = True
        result += cipher.encrypt(chunk)
    return base64.b64encode(result).decode('utf-8')

def decrypt(in_str, password, salt_header='Salted__', key_length=32):
    in_str = base64.b64decode(in_str)
    bs = AES.block_size
    offset = 0
    salt = in_str[:bs][len(salt_header):]
    offset += bs
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    result = b''
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(
            in_str[offset:offset+(1024*bs)])
        offset += (1024*bs)
        if len(next_chunk) == 0:
            padding_length = chunk[-1]
            chunk = chunk[:-padding_length]
            finished = True 
        result += (bytes(x for x in chunk))
    return result