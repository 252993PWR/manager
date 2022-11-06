from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import requests
import uuid as uid
from passlib.hash import pbkdf2_sha512
import base64
import binascii
import random

from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util.Padding import pad, unpad
from Crypto.Protocol.KDF import PBKDF2

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
import manager.orgAccounts
