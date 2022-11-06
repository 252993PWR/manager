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

        uuid = str(uid.uuid4())
        orgPassHash = pbkdf2Hash(orgPass)

        query="""
            INSERT INTO organizations (uuid,name,code,password)
            VALUES(%s,%s,%s,%s)"""
        cursor.execute(query,
        [uuid,
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
