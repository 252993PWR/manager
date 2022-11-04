from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import uuid as uid

from manager import *

# app = Flask(__name__)
#
# app.secret_key = 'SXQW4FtoQ_W_6@ThNeq2@LLmTqbW945'
#
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'admin'
# app.config['MYSQL_PASSWORD'] = '8k3MJI0bKZRqiDVbzaiy'
# app.config['MYSQL_DB'] = 'manager'
#
# mysql = MySQL(app)
#
# defaultUrl = "http://localhost:5000"

# @app.route('/api/login', methods=['POST'])
# def my_test_endpoint():
#     input_json = request.get_json(force=True)
#     # force=True, above, is necessary if another developer
#     # forgot to set the MIME type to 'application/json'
#     print 'data from client:', input_json
#     dictToReturn = {'answer':42}
#     return jsonify(dictToReturn)

@app.route('/')
def mainPage():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
