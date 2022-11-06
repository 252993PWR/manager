from manager import *

def pbkdf2Hash(txt, *args, **kwargs):
    salt = kwargs.get('salt', None)
    if not salt:
        salt="7a440e4b992e447e97da57dbbaa03b251a2b964e2bdd42e3ab957d96da585d7d5ce1dbc48091454bb35910a2159c7e7a5ce1dbc48091454bb35910a2159c7e7a"
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

def getKeyC(cipherToken,tempToken,tokenSalt,userUUID):
    cursor = mysql.connection.cursor()
    query="""
        SELECT * FROM users
        WHERE uuid LIKE %s
        LIMIT 1"""
    cursor.execute(query,
    [userUUID])
    keyB = cursor.fetchone()[2]
    cursor.close()
    keyA = getKeyA(cipherToken,tempToken,tokenSalt)
    # print(keyB)
    # print()
    # print(keyA)
    return aesDecrypt(keyB, keyA)

def getKeyA(cipherToken,tempToken,tokenSalt):
    return aesDecrypt(hexToBytes(cipherToken),pbkdf2Hash(tempToken,tokenSalt))

def bytesToHex(byteValue):
    return binascii.hexlify(byteValue).decode('ascii')

def hexToBytes(hexValue):
    return binascii.unhexlify(hexValue.encode('ascii'))

def generateRandomName(seed, *args, **kwargs):
    len = kwargs.get('len', 3)
    sep = kwargs.get('sep', '-')
    output = seed.lower()[:len]+str(sep)+str(uid.uuid4().hex)[:4]
    return output

def generatePass(length):
    characters="abcdefghijklmnopqrstuvwxyz!@#$&*ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    while(True):
        passw=''.join(random.choice(characters) for i in range(length))
        reg = r'(?=.*[0-9])(?=.*[a-z])(?=.*[!@#$&*])(?=.*[A-Z]).{' + re.escape(str(length)) + r',}$'
        if re.match(reg, passw):
            break
    return passw
