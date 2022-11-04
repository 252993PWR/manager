from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import uuid as uid

from manager import *

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
            WHERE users.uuid=%s"""
        cursor.execute(query, [session['uuid']])
        passwords = cursor.fetchall()
        cursor.close()
        print(passwords)
        return render_template('home.html',
        data=passwords)
    else:
        return render_template('loginForm.html')

@app.route('/viewPass',methods=['POST'], endpoint='viewPass')
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
            query="""
                INSERT INTO passwords
                (savedPassword,
                uuid,
                userUUID,
                isKey)
                VALUES
                (%s,%s,%s,%s)"""
            cursor.execute(query,
                [request.form['savedPassword'],
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
