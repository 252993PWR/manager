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

import manager.accounts
import manager.passwords
