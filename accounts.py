from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import uuid as uid

from manager import *

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

        query="""
            INSERT INTO users (username,keyB,uuid)
            VALUES(%s,%s,%s)"""
        cursor.execute(query,
        [input_json['username'],
        input_json['password'],
        uuid])
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
    if dictFromServer['error']:
        return render_template('loginForm.html',
        msg=dictFromServer['msg'],
        error=dictFromServer['error'])
    else:
        session['loggedin'] = True
        session['uuid'] = dictFromServer['uuid']
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
        query="""
            SELECT * FROM users
            WHERE username LIKE %s AND keyB LIKE %s
            LIMIT 1"""
        cursor.execute(query,
        [input_json['username'],
        input_json['password']])
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

@app.route('/logout', endpoint='logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('passUUID', None)
    session.pop('uuid', None)
    return redirect(url_for('home'))
