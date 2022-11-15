from manager import *
from manager.misc import *

@app.route('/orgManage', methods=['POST'], endpoint='orgManage')
def orgManage():
    err="0"
    msg="OK"
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        query="""
            SELECT * FROM usersOrganizations
            WHERE userUUID LIKE %s"""
        cursor.execute(query,[session['uuid']])
        isAdmin=cursor.fetchone()[3]
        if isAdmin:
            if request.form['action'] == 'manageHome' or request.form['action'] == 'deleteUser':
                cursor = mysql.connection.cursor()
                queryGetUsers="""
                    SELECT
                    users.uuid,
                    users.username,
                    usersInfo.firstName,
                    usersInfo.secondName,
                    usersInfo.orgMail,
                    usersOrganizations.orgUUID FROM users
                    JOIN usersOrganizations on users.uuid=usersOrganizations.userUUID
                    JOIN usersInfo on users.uuid=usersInfo.userUUID
                    WHERE usersOrganizations.orgUUID=%s AND NOT usersOrganizations.isAdmin"""
                cursor.execute(queryGetUsers, [session['orgUUID']])
                orgUsers = cursor.fetchall()
                cursor.close()
                if request.form['action'] == 'deleteUser':
                    deleted=False
                    for user in orgUsers:
                        if request.form['userUUID']==user[0]:
                            deleted=True
                            cursor = mysql.connection.cursor()
                            cursor.execute("""
                                DELETE FROM users WHERE users.uuid=%s""",
                                [request.form['userUUID']])
                            mysql.connection.commit()
                            cursor = mysql.connection.cursor()
                            cursor.execute(queryGetUsers, [session['orgUUID']])
                            orgUsers = cursor.fetchall()
                            cursor.close()
                    if not deleted:
                        err="1"
                        msg="Deletion failed - User does not exist in your organization"
                return render_template('orgManage.html',
                data=tuple(orgUsers),
                action='manageHome',
                msg=msg,
                err=err)
            elif request.form['action'] == 'addUser':
                return render_template('orgManage.html',
                action='addUser',
                msg=msg,
                err=err)
            elif request.form['action'] == 'applyAddUser':
                print('XXX')
                # Add admin user
                username=generateRandomName('user',len=4)
                userPass=request.form['savedPassword']

                uuid = str(uid.uuid4())

                keyC = generateKeyC()
                keyA = pbkdf2Hash(userPass)
                keyB = aesEncrypt(keyC, keyA)

                query="""
                    INSERT INTO users (username,keyB,uuid)
                    VALUES(%s,%s,%s)"""
                cursor = mysql.connection.cursor()
                cursor.execute(query,
                [username,
                keyB,
                uuid])
                mysql.connection.commit()

                query="""
                    INSERT INTO usersOrganizations (userUUID, orgUUID, isAdmin)
                    VALUES(%s,%s,%s)"""
                cursor.execute(query,
                [uuid,
                session['orgUUID'],
                '0'])
                mysql.connection.commit()

                query="""
                    INSERT INTO usersInfo (userUUID, firstName, secondName, orgMail)
                    VALUES(%s,%s,%s,%s)"""
                cursor.execute(query,
                [uuid,
                request.form['firstName'],
                request.form['secondName'],
                request.form['orgMail']])
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

                msg='User successfully created'

                return render_template('orgManage.html',
                action='applyAddUser',
                msg=msg,
                err=err,
                username=username,
                userPass=userPass,
                firstName=request.form['firstName'],
                secondName=request.form['secondName'],
                orgMail=request.form['orgMail'])
            else:
                return render_template('orgLoginForm.html')
                # return redirect(url_for('home'))
                # abort(403, description="Access forbidden")
                # return redirect(url_for('home'))
    else:
        return render_template('orgLoginForm.html')
