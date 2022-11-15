from manager import *
from manager.misc import *

@app.route('/home', endpoint='home')
def home():
    # Remove session data, this will log the user out
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        query="""
            SELECT
            passwords.uuid,
            passwords.savedPassword,
            passwordsInfo.name,
            passwordsInfo.username FROM users
            JOIN passwords on users.uuid=passwords.userUUID
            JOIN passwordsInfo on passwords.uuid=passwordsInfo.passUUID
            WHERE users.uuid=%s AND NOT passwords.isKey"""
        cursor.execute(query, [session['uuid']])
        passwords = cursor.fetchall()
        passList=[[x for x in p] for p in passwords]
        #print(passList)
        cursor.close()

        cursor = mysql.connection.cursor()
        query="""
            SELECT * FROM usersOrganizations
            WHERE userUUID LIKE %s LIMIT 1"""
        cursor.execute(query,[session['uuid']])
        usr = cursor.fetchone()
        if usr:
            isAdmin=usr[3]
        else:
            isAdmin=0

        for i,p in enumerate(passwords):
            tokenSalt="d586780483a24f5eb45a8124eb55791582788754e6a64fea945762ce40b64444ef8e03805b1e45b9bdc675bac51cb23d59b887094d1c4611b95ddbd741fe5237"
            keyC = getKeyC(session['cipherToken'],session['tempToken'],tokenSalt,session['uuid'])
            passList[i][1]=aesDecrypt(p[1],keyC).decode('ascii')
        return render_template('home.html',
        data=tuple(passList),
        isAdmin=isAdmin)
    else:
        return render_template('loginForm.html')

@app.route('/viewPass',methods=['POST'], endpoint='viewPass')
def viewPass():
    if 'loggedin' in session:
        print(session)
        cursor = mysql.connection.cursor()
        uuid = request.form['passUUID']

        tokenSalt="d586780483a24f5eb45a8124eb55791582788754e6a64fea945762ce40b64444ef8e03805b1e45b9bdc675bac51cb23d59b887094d1c4611b95ddbd741fe5237"
        keyC = getKeyC(session['cipherToken'],session['tempToken'],tokenSalt,session['uuid'])

        if request.form['action'] == 'applyEdit':
            passw = request.form['savedPassword'].encode('ascii')
            query="""
                UPDATE
                passwords,
                passwordsInfo
                SET passwords.savedPassword=%s,
                passwordsInfo.name=%s,
                passwordsInfo.username=%s,
                passwordsInfo.pageURL=%s,
                passwordsInfo.note=%s
                WHERE passwords.uuid=%s AND
                passwords.userUUID=%s AND
                passwordsInfo.passUUID=%s"""
            cursor.execute(query,
                [aesEncrypt(passw,keyC),
                request.form['passName'],
                request.form['passUsername'],
                request.form['passPageURL'],
                request.form['passNote'],
                request.form['passUUID'],
                session['uuid'],
                request.form['passUUID']])
            mysql.connection.commit()

        elif request.form['action'] == 'applyAdd':
            passw = request.form['savedPassword'].encode('ascii')
            uuid = str(uid.uuid4())
            query="""
                INSERT INTO passwords
                (savedPassword,
                uuid,
                userUUID,
                isKey)
                VALUES
                (%s,%s,%s,%s)"""
            cursor.execute(query,
                [aesEncrypt(passw,keyC),
                uuid,
                session['uuid'],
                '0'])
            mysql.connection.commit()
            query="""
                INSERT INTO passwordsInfo
                (passUUID,
                name,
                username,
                pageURL,
                note)
                VALUES
                (%s,%s,%s,%s,%s)"""
            cursor.execute(query,
                [uuid,
                request.form['passName'],
                request.form['passUsername'],
                request.form['passPageURL'],
                request.form['passNote']])
            mysql.connection.commit()

        query="""
            SELECT
            passwords.uuid,
            passwords.savedPassword,
            passwordsInfo.name,
            passwordsInfo.username,
            passwordsInfo.pageURL,
            passwordsInfo.note FROM users
            JOIN passwords on users.uuid=passwords.userUUID
            JOIN passwordsInfo on passwords.uuid=passwordsInfo.passUUID
            WHERE passwords.UUID=%s AND
            users.uuid=%s LIMIT 1"""
        cursor.execute(query, [uuid,session['uuid']])
        print("XXXX")

        password = cursor.fetchone()
        cursor.close()
        #print(password)
        #print(request.form['action'])

        tokenSalt="d586780483a24f5eb45a8124eb55791582788754e6a64fea945762ce40b64444ef8e03805b1e45b9bdc675bac51cb23d59b887094d1c4611b95ddbd741fe5237"
        keyC = getKeyC(session['cipherToken'],session['tempToken'],tokenSalt,session['uuid'])
        passw = password[1]

        return render_template('viewPass.html',
            passUUID=password[0],
            savedPassword=aesDecrypt(passw,keyC).decode('ascii'),
            passName=password[2],
            passUsername=password[3],
            passPageURL=password[4],
            passNote=password[5],
            action=request.form['action'])
    else:
        return render_template('loginForm.html')

@app.route('/addPass',methods=['POST'],endpoint='addPass')
def addPass():
    if 'loggedin' in session:
        if request.form['action']=='add':
            return render_template('addPass.html',
            action=request.form['action'])
    else:
        return render_template('loginForm.html')

@app.route('/deletePass',methods=['POST'],endpoint='deletePass')
def deletePass():
    if 'loggedin' in session:
        if request.form['action']=="delete":
            cursor = mysql.connection.cursor()
            cursor.execute("""
                DELETE FROM passwords WHERE passwords.uuid=%s""",
                [request.form['passUUID']])
            mysql.connection.commit()
            return redirect(url_for('home'))
    else:
        return render_template('loginForm.html')
