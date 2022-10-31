from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import uuid as uid

app = Flask(__name__)

app.secret_key = 'SXQW4FtoQ_W_6@ThNeq2@LLmTqbW945'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = '8k3MJI0bKZRqiDVbzaiy'
app.config['MYSQL_DB'] = 'manager'

mysql = MySQL(app)

defaultUrl = "http://localhost:5000"

# @app.route('/api/login', methods=['POST'])
# def my_test_endpoint():
#     input_json = request.get_json(force=True)
#     # force=True, above, is necessary if another developer
#     # forgot to set the MIME type to 'application/json'
#     print 'data from client:', input_json
#     dictToReturn = {'answer':42}
#     return jsonify(dictToReturn)

@app.route('/registerForm')
def registerForm():
    return render_template('registerForm.html')

@app.route('/loginForm')
def loginForm():
    return render_template('loginForm.html')

@app.route('/')
def mainPage():
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
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
    #return 'Your email:'+str(dictFromServer['username'])
    return render_template('registerForm.html',
    msg=dictFromServer['msg'],
    error=dictFromServer['error'])
    #email=dictFromServer['username'],
    #password=dictFromServer['password'])
        # name = request.form['name']
        # password = request.form['password']
        # cursor = mysql.connection.cursor()
        # cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,password))
        # mysql.connection.commit()
        # cursor.close()
        #return f"Done!!"

@app.route('/api/register', methods=['POST'])
def apiRegister():
    # Here you do things on database etc.
    input_json = request.get_json(force=True)
    print('data from client:', input_json)
    dictToReturn = {}
    cursor = mysql.connection.cursor()
    # Check if account already exist
    cursor.execute("SELECT * FROM users WHERE username LIKE %s", [input_json['username']])
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
    elif not re.match(r'(?=.*[0-9])(?=.*[a-z])(?=.*[!@#$&*])(?=.*[A-Z]).{8,}$', input_json['password']):
        dictToReturn['error']=4
        dictToReturn['msg'] = '''
        Weak password!<br><br>
        Your password should have:<br>
        - at least one special character: !@#$&*<br>
        - at least one digit<br>
        - at least one lowercase letter<br>
        - length of at least 8<br>
        '''
    elif not input_json['password'] == input_json['confPassword']:
        dictToReturn['error']=5
        dictToReturn['msg'] = 'Passwords are not identical!'
    else:
        uuid = str(uid.uuid4())
        cursor.execute(''' INSERT INTO users (username,keyB,uuid) VALUES(%s,%s,%s)''',(input_json['username'],input_json['password'],uuid))
        mysql.connection.commit()
        dictToReturn['error']=0
        dictToReturn['msg']='Account successfully created!'
    cursor.close()
    return jsonify(dictToReturn)

@app.route('/login',methods=['POST'])
def login():
    dictToSend = {
        'username':request.form['username'],
        'password':request.form['password'],
    }
    res = requests.post('http://localhost:5000/api/login', json=dictToSend)
    print('response from server:',res.text)
    dictFromServer = res.json()
    #return 'Your email:'+str(dictFromServer['username'])
    if dictFromServer['error']:
        return render_template('loginForm.html',
        msg=dictFromServer['msg'],
        error=dictFromServer['error'])
    else:
        session['loggedin'] = True
        session['uuid'] = dictFromServer['uuid']
        return redirect(url_for('home'))

@app.route('/api/login', methods=['POST'])
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
        cursor.execute("SELECT * FROM users WHERE username LIKE %s AND keyB LIKE %s LIMIT 1", [input_json['username'], input_json['password']])
        account = cursor.fetchone()
        cursor.close()
        if account:
            dictToReturn['error']=0
            dictToReturn['uuid'] = account[3]
            dictToReturn['msg'] = 'Successfully logged in!'
        else:
            dictToReturn['error']=2
            dictToReturn['msg'] = 'Wrong email or password'
    return jsonify(dictToReturn)

@app.route('/home')
def home():
    # Remove session data, this will log the user out
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("""
        SELECT
            passwords.uuid,
            passwords.savedPassword,
            passwordsInfo.name,
            passwordsInfo.username FROM users
            JOIN passwords on users.uuid=passwords.userUUID
            JOIN passwordsInfo on passwords.uuid=passwordsInfo.passUUID
            WHERE users.uuid=%s""", [session['uuid']])
        passwords = cursor.fetchall()
        cursor.close()
        print(passwords)
        return render_template('home.html',
        data=passwords)
    else:
        return render_template('loginForm.html')

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('passUUID', None)
    session.pop('uuid', None)
    return redirect(url_for('home'))

@app.route('/viewPass',methods=['POST'])
def viewPass():
    #print(request.headers)
    if 'loggedin' in session:
        print(session)
        # session['passUUID']=request.form['passUUID']
        # dictToSend = {
        #     'passUUID':request.form['passUUID'],
        # }
        #print('xxxx')
        # res = requests.post('http://localhost:5000/api/viewPass', json=dictToSend)
        # print('response from server:',res.text)
        # dictFromServer = res.json()
        # Remove session data, this will log the user out
        cursor = mysql.connection.cursor()
        uuid = request.form['passUUID']
        if request.form['action'] == 'applyEdit':
            cursor.execute("""
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
                passwordsInfo.passUUID=%s""",
                [request.form['savedPassword'],
                request.form['passName'],
                request.form['passUsername'],
                request.form['passPageURL'],
                request.form['passNote'],
                request.form['passUUID'],
                session['uuid'],
                request.form['passUUID']])
            mysql.connection.commit()
        elif request.form['action'] == 'applyAdd':
            uuid = str(uid.uuid4())
            cursor.execute("""
                INSERT INTO passwords
                (savedPassword,
                uuid,
                userUUID,
                isKey)
                VALUES
                (%s,%s,%s,%s)""",
                [request.form['savedPassword'],
                uuid,
                session['uuid'],
                '0'])
            mysql.connection.commit()
            cursor.execute("""
                INSERT INTO passwordsInfo
                (passUUID,
                name,
                username,
                pageURL,
                note)
                VALUES
                (%s,%s,%s,%s,%s)""",
                [uuid,
                request.form['passName'],
                request.form['passUsername'],
                request.form['passPageURL'],
                request.form['passNote']])
            mysql.connection.commit()
        cursor.execute("""
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
            users.uuid=%s LIMIT 1""", [uuid,session['uuid']])
        password = cursor.fetchone()
        cursor.close()
        print(password)
        print(request.form['action'])
        return render_template('viewPass.html',
        passUUID=password[0],
        savedPassword=password[1],
        passName=password[2],
        passUsername=password[3],
        passPageURL=password[4],
        passNote=password[5],
        action=request.form['action'])
    else:
        return render_template('loginForm.html')

@app.route('/addPass',methods=['POST'])
def addPass():
    if 'loggedin' in session:
        if request.form['action']=='add':
            return render_template('addPass.html',
            action=request.form['action'])
    else:
        return render_template('loginForm.html')

@app.route('/deletePass',methods=['POST'])
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

# @app.route('/api/viewPass')
# def apiViewPass():
#     input_json = request.get_json(force=True)
#     print('data from client:', input_json)
#     dictToReturn = {}
#     if 'loggedin' in session:
#         cursor = mysql.connection.cursor()
#         cursor.execute("""
#             SELECT
#             passwords.uuid,
#             passwords.savedPassword,
#             passwordsInfo.name,
#             passwordsInfo.username,
#             passwordsInfo.pageURL,
#             passwordsInfo.note FROM users
#             JOIN passwords on users.uuid=passwords.userUUID
#             JOIN passwordsInfo on passwords.uuid=passwordsInfo.passUUID
#             WHERE passwords.UUID=%s AND
#             users.uuid=%s LIMIT 1""", [input_json['passUUID'],session['uuid']])
#         password = cursor.fetchone()
#         print(password)
#         cursor.close()
#         dictToReturn['passUUID']=password[0]
#         dictToReturn['savedPassword']=password[1]
#         dictToReturn['passName']=password[2]
#         dictToReturn['passUsername']=password[3]
#         dictToReturn['passPageURL']=password[4]
#         dictToReturn['passNote']=password[5]
#         print(password)
#         return jsonify(dictToReturn)
#     else:
#         return render_template('loginForm.html')
#
#     return jsonify(dictToReturn)

# @app.route('/api/logout',methods=['POST'])
# def logout():
#     # Remove session data, this will log the user out
#     session.pop('loggedin', None)
#     session.pop('uuid', None)
#     session.pop('username', None)
#     # Redirect to login page
#     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
