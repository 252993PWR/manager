from manager import *

salt="7a440e4b992e447e97da57dbbaa03b251a2b964e2bdd42e3ab957d96da585d7d5ce1dbc48091454bb35910a2159c7e7a5ce1dbc48091454bb35910a2159c7e7a"

def pbkdf2Hash(txt):
    return PBKDF2(txt, salt, 64, 50000)

def generateKeyC():
    return pbkdf2Hash(str(uid.uuid4().hex))

def aesEncrypt(value, key):
    value = base64.b64encode(value)
    key = pad(key, AES.block_size)[:32]
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(value, AES.block_size))
    return (iv + ciphertext)

def aesDecrypt(encrypted_value, key):
    key = pad(key, AES.block_size)[:32]
    iv = encrypted_value[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64decode(cipher.decrypt(encrypted_value[AES.block_size:]))
