from manager import *
from manager.misc import *

@app.route('/registerForm', endpoint='registerForm')
def registerForm():
    return render_template('registerForm.html')

@app.route('/loginForm', endpoint='loginForm')
def loginForm():
    return render_template('loginForm.html')

@app.route('/register', methods=['POST'], endpoint='register')
def register():
    # Here you send data needed to do things
    dictToSend = {
        'username':request.form['username'],
        'password':request.form['password'],
        'confPassword':request.form['confPassword']
    }
    res = requests.post('http://localhost:5000/api/register', json=dictToSend)
    print('response from server:',res.text)
    dictFromServer = res.json()
    return render_template('registerForm.html',
    msg=dictFromServer['msg'],
    error=dictFromServer['error'])

@app.route('/api/register', methods=['POST'], endpoint='apiRegister')
def apiRegister():
    # Here you do things on database etc.
    input_json = request.get_json(force=True)
    print('data from client:', input_json)
    dictToReturn = {}
    cursor = mysql.connection.cursor()
    # Check if account already exist
    query="""
        SELECT * FROM users
        WHERE username LIKE %s"""
    cursor.execute(query, [input_json['username']])
    account = cursor.fetchone()
    if not input_json['password'] or not input_json['username'] or not input_json['confPassword']:
        dictToReturn['error']=1
        dictToReturn['msg'] = 'Please fill out the form!'
    elif not re.match(r'^[\w\-\.]+@([\w\-]+\.)+[\w\-]{2,4}$', input_json['username']):
        dictToReturn['error']=2
        dictToReturn['msg'] = 'Invalid email address!'
    elif account:
        dictToReturn['error']=3
        dictToReturn['msg'] = 'Account already exist!'
    elif not re.match(r'(?=.*[0-9])(?=.*[a-z])(?=.*[!@#$&*])(?=.*[A-Z]).{12,}$', input_json['password']):
        dictToReturn['error']=4
        dictToReturn['msg'] = '''
        <b>Weak password!</b><br><br>
        Your password should have:<br>
        - at least one special character: !@#$&*<br>
        - at least one digit<br>
        - at least one lowercase letter<br>
        - length of at least 12<br>
        '''
    elif not input_json['password'] == input_json['confPassword']:
        dictToReturn['error']=5
        dictToReturn['msg'] = 'Passwords are not identical!'
    else:
        uuid = str(uid.uuid4())

        keyC = generateKeyC()
        keyA = pbkdf2Hash(input_json['password'])
        keyB = aesEncrypt(keyC, keyA)
        #check = aesDecrypt(keyB, keyA)
        # print()
        # print(len(keyA))
        # print(keyA)
        # print()
        # print(len(keyB))
        # print(keyB)
        # print()
        # print(len(keyC))
        # print(keyC)
        # print()

        #a=1/0
        query="""
            INSERT INTO users (username,keyB,uuid)
            VALUES(%s,%s,%s)"""
        cursor.execute(query,
        [input_json['username'],
        keyB,
        uuid])
        mysql.connection.commit()

        userPassword = aesEncrypt(keyA, keyC)
        passUUID = str(uid.uuid4())

        query="""
            INSERT INTO passwords
            (savedPassword,
            uuid,
            userUUID,
            isKey)
            VALUES
            (%s,%s,%s,%s)"""
        cursor.execute(query,
            [userPassword,
            passUUID,
            uuid,
            '1'])
        mysql.connection.commit()

        dictToReturn['error']=0
        dictToReturn['msg']='Account successfully created!'
    cursor.close()
    return jsonify(dictToReturn)

@app.route('/login',methods=['POST'],endpoint='login')
def login():
    dictToSend = {
        'username':request.form['username'],
        'password':request.form['password'],
    }
    res = requests.post('http://localhost:5000/api/login', json=dictToSend)
    print('response from server:',res.text)
    dictFromServer = res.json()
    #return 'Your email:'+str(dictFromServer['username'])
    # session['loggedin'] = True
    # session['uuid'] = "13cc6720-917a-4d03-b5d6-8c033ef9948e"
    # return redirect(url_for('home'))
    if dictFromServer['error']:
        return render_template('loginForm.html',
        msg=dictFromServer['msg'],
        error=dictFromServer['error'])
    else:
        session['loggedin'] = True
        dictFromServer.pop('msg',None)
        dictFromServer.pop('error',None)
        for key in dictFromServer.keys():
            #print(key)
            session[key]=dictFromServer[key]
        return redirect(url_for('home'))

@app.route('/api/login', methods=['POST'], endpoint='apiLogin')
def apiLogin():
    input_json = request.get_json(force=True)
    print('data from client:', input_json)
    dictToReturn = {}
    dictToReturn['error']=0
    dictToReturn['msg']='IT WORKS!'
    cursor = mysql.connection.cursor()
    if not input_json['password'] or not input_json['username']:
        dictToReturn['error']=1
        dictToReturn['msg'] = 'Please fill out the form!'
    else:

        # keyC = generateKeyC()
        # keyA = pbkdf2Hash(input_json['password'])
        # keyB = base64.b64encode(aesEncrypt(keyC, keyA)).decode('ascii')
        # #check = aesDecrypt(keyB, keyA)
        # print(len(keyB))
        # print(keyB)
        #
        query="""
            SELECT * FROM users
            WHERE username LIKE %s
            LIMIT 1"""
        cursor.execute(query,
        [input_json['username']])
        account = cursor.fetchone()
        cursor.close()
        if account:
            cursor = mysql.connection.cursor()
            query="""
                SELECT
                passwords.uuid,
                passwords.savedPassword,
                passwords.isKey FROM passwords
                WHERE passwords.userUUID=%s AND passwords.isKey"""
            cursor.execute(query, [account[3]])
            try:
                userPassword = cursor.fetchone()[1]
            except TypeError:
                pass

            # keyA1 = pbkdf2Hash(input_json['password'])
            # keyB1 = account[2]
            # keyC1 = decryptFromDB(account[2], keyA1)

            # print()
            # print(str(uid.uuid4().hex))

            #keyB = base64.b64encode(aesEncrypt(keyC, keyA)).decode('ascii')

            try:
                keyA1 = pbkdf2Hash(input_json['password'])
                keyB1 = account[2]
                keyC1 = aesDecrypt(account[2], keyA1)

                keyA2 = aesDecrypt(userPassword,keyC1)
                if keyA2 == keyA1:
                    tokenSalt="d586780483a24f5eb45a8124eb55791582788754e6a64fea945762ce40b64444ef8e03805b1e45b9bdc675bac51cb23d59b887094d1c4611b95ddbd741fe5237"
                    tempToken = str(uid.uuid4().hex)
                    token = pbkdf2Hash(tempToken,tokenSalt)
                    cipherToken = aesEncrypt(keyA1, token)
                    dictToReturn['error']=0
                    dictToReturn['uuid'] = account[3]
                    dictToReturn['msg'] = 'Successfully logged in!'
                    dictToReturn['cipherToken'] = bytesToHex(cipherToken)
                    dictToReturn['tempToken'] = tempToken
                else:
                    dictToReturn['error']=2
                    dictToReturn['msg'] = 'Wrong email or password'
            except binascii.Error as err:
                dictToReturn['error']=2
                dictToReturn['msg'] = 'Wrong email or password'
            except ValueError:
                dictToReturn['error']=2
                dictToReturn['msg'] = 'Wrong email or password'

            # keyB1 = base64.b64encode(aesEncrypt(keyC, keyA)).decode('ascii')
            #
            # userPassword = base64.b64encode(aesEncrypt(keyA, keyC)).decode('ascii')
            # keyA = aesDecrypt(base64.b64decode(userPassword.encode('ascii')), keyC)
            #
            # print(password)
        else:
            dictToReturn['error']=2
            dictToReturn['msg'] = 'Wrong email or password'
    return jsonify(dictToReturn)

@app.route('/logout', endpoint='logout')
def logout():
    # Remove session data, this will log the user out
    sess=dict(session)
    for key in sess.keys():
        session.pop(key, None)
    if 'orgUUID' in sess:
        return redirect(url_for('orgLoginForm'))
    else:
        return redirect(url_for('loginForm'))
