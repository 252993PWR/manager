from manager import *
from manager.misc import *

@app.route('/orgRegisterForm', endpoint='orgRegisterForm')
def registerForm():
    return render_template('orgRegisterForm.html')

@app.route('/orgLoginForm', endpoint='orgLoginForm')
def orgLoginForm():
    return render_template('orgLoginForm.html')

@app.route('/orgRegister', methods=['POST'], endpoint='orgRegister')
def orgRegister():
    # Here you send data needed to do things
    dictToSend = {
        'orgName':request.form['orgName']
        #'confirmationMail':request.form['confirmationName']
    }
    res = requests.post('http://localhost:5000/api/orgRegister', json=dictToSend)
    print('response from server:',res.text)
    dictFromServer = res.json()
    return render_template('orgRegisterForm.html',
    msg=dictFromServer['msg'],
    error=dictFromServer['error'])

@app.route('/api/orgRegister', methods=['POST'], endpoint='orgApiRegister')
def orgApiRegister():
    # Here you do things on database etc.
    input_json = request.get_json(force=True)
    print('data from client:', input_json)
    dictToReturn = {}
    cursor = mysql.connection.cursor()
    # Check if account already exist
    if not input_json['orgName']:
        dictToReturn['error']=1
        dictToReturn['msg'] = 'Please fill out the form!'
    elif not re.match(r'^[a-zA-Z0-9]{3,}$', input_json['orgName']):
        dictToReturn['error']=2
        dictToReturn['msg'] = '''
        Wrong organization name!<br>
        - Organization name should be at least 3 character long<br>
        - No special characters are allowed
        '''
    else:
        # Add organization
        orgName=input_json['orgName']
        orgCode=generateRandomName(input_json['orgName'])
        orgPass=generatePass(6)

        orgUUID = str(uid.uuid4())
        orgPassHash = pbkdf2Hash(orgPass)

        query="""
            INSERT INTO organizations (uuid,name,code,password)
            VALUES(%s,%s,%s,%s)"""
        cursor.execute(query,
        [orgUUID,
        orgName,
        orgCode,
        orgPassHash])
        mysql.connection.commit()

        # Add admin user
        adminUsername=generateRandomName('admin',len=5,sep='-')
        adminPass=generatePass(12)

        uuid = str(uid.uuid4())

        keyC = generateKeyC()
        keyA = pbkdf2Hash(adminPass)
        keyB = aesEncrypt(keyC, keyA)

        query="""
            INSERT INTO users (username,keyB,uuid)
            VALUES(%s,%s,%s)"""
        cursor.execute(query,
        [adminUsername,
        keyB,
        uuid])
        mysql.connection.commit()

        query="""
            INSERT INTO usersOrganizations (userUUID, orgUUID, isAdmin)
            VALUES(%s,%s,%s)"""
        cursor.execute(query,
        [uuid,
        orgUUID,
        '1'])
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
        dictToReturn['msg']='''
        Organization and default admin account successfully created!<br>
        <b><u>Write down your access credentials:</u></b><br><br>
        <b>Known for all members:<br>
        - Organization code:</b> {0}<br>
        - <b>Organization password:</b> {1}<br><br>
        <b>Known only for organization administrator (you):<br>
        - Admin username:</b> {2}<br>
        - <b>Admin password:</b> {3}<br>
        '''.format(orgCode, orgPass, adminUsername, adminPass)

    cursor.close()
    return jsonify(dictToReturn)


@app.route('/orgLogin',methods=['POST'],endpoint='orgLogin')
def orgLogin():
    dictToSend = {
        'orgCode':request.form['orgCode'],
        'orgPass':request.form['orgPass'],
        'username':request.form['username'],
        'password':request.form['password'],
    }
    print('xxx')
    res = requests.post('http://localhost:5000/api/orgLogin', json=dictToSend)
    print('response from server:',res.text)
    dictFromServer = res.json()
    if dictFromServer['error']:
        return render_template('orgLoginForm.html',
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

@app.route('/api/orgLogin', methods=['POST'], endpoint='orgApiLogin')
def orgApiLogin():
    input_json = request.get_json(force=True)
    print('data from client:', input_json)
    dictToReturn = {}
    dictToReturn['error']=0
    dictToReturn['msg']='IT WORKS!'
    cursor = mysql.connection.cursor()
    if not input_json['orgCode'] or not input_json['orgPass'] or not input_json['username'] or not input_json['password']:
        dictToReturn['error']=1
        dictToReturn['msg'] = 'Please fill out the form!'
    else:
        # Check org
        cursor = mysql.connection.cursor()
        query="""
            SELECT * FROM organizations
            WHERE code LIKE %s
            LIMIT 1"""
        cursor.execute(query,
        [input_json['orgCode']])
        org = cursor.fetchone()

        # Check org username
        cursor = mysql.connection.cursor()
        query="""
            SELECT * FROM users
            WHERE username LIKE %s
            LIMIT 1"""
        cursor.execute(query,
        [input_json['username']])
        account = cursor.fetchone()

        if account and org:
            # Check org pass
            orgPassHash1=org[4]
            orgPassHash2=pbkdf2Hash(input_json['orgPass'])
            orgAccess=(orgPassHash1==orgPassHash2)

            # Check org user pass
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

            try:
                keyA1 = pbkdf2Hash(input_json['password'])
                keyB1 = account[2]
                keyC1 = aesDecrypt(account[2], keyA1)

                keyA2 = aesDecrypt(userPassword,keyC1)
                if keyA2 == keyA1 and orgAccess:
                    tokenSalt="d586780483a24f5eb45a8124eb55791582788754e6a64fea945762ce40b64444ef8e03805b1e45b9bdc675bac51cb23d59b887094d1c4611b95ddbd741fe5237"
                    tempToken = str(uid.uuid4().hex)
                    token = pbkdf2Hash(tempToken,tokenSalt)
                    cipherToken = aesEncrypt(keyA1, token)
                    dictToReturn['error']=0
                    dictToReturn['uuid'] = account[3]
                    dictToReturn['msg'] = 'Successfully logged in!'
                    dictToReturn['cipherToken'] = bytesToHex(cipherToken)
                    dictToReturn['tempToken'] = tempToken
                    dictToReturn['orgUUID'] = org[1]
                else:
                    dictToReturn['error']=2
                    dictToReturn['msg'] = 'Wrong credentials'
            except binascii.Error as err:
                dictToReturn['error']=2
                dictToReturn['msg'] = 'Wrong credentials'
            except ValueError:
                dictToReturn['error']=2
                dictToReturn['msg'] = 'Wrong credentials'

        else:
            dictToReturn['error']=2
            dictToReturn['msg'] = 'Wrong credentials'
    return jsonify(dictToReturn)
