from flask import Flask, request, abort, send_file
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
import pymysql
from hashlib import md5, sha256
from string import ascii_letters, digits
from random import choices
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@localhost/treasure'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app, support_credentials=True)

db = SQLAlchemy(app)

class Keys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), unique=True, nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=True)
    timestamp = db.Column(db.Integer, nullable=False)
    
pymysql.install_as_MySQLdb()
db.create_all()


def generate_key():
    return ''.join(choices(ascii_letters + digits, k=64))

def get_cipher(password):
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length = 32,
        salt = b'\xd6\xd8\xcb\xc3\xee3?r\xb0VQ\xa4\xb3\xc0!H',
        iterations = 100000,
        backend = default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    return f

def shift_chars(text):
    shifted = ''
    shift = 4218
    for char in text:
        shifted += chr(char + shift)
    return shifted.encode('utf-8')

def unshift_chars(text):
    unshifted = ''
    shift = 4218
    for char in text:
        unshifted += chr(ord(char) - shift)
    return unshifted

def encrypt_text(text, key):
    cipher = get_cipher(key)
    encrypted_text = cipher.encrypt(text.encode())
    
    return encrypted_text

def md5_hex(text):
    if isinstance(text, str):
        text = text.encode()
    return md5(text).hexdigest()

def sha256_hex(text):
    if isinstance(text, str):
        text = text.encode()
    return sha256(text).hexdigest()

def get_current_timestamp():
    return int(time.time())

def hash_password(password):
    if password:
        return md5(password.encode()).hexdigest()
    return None

def decrypt_text(text, key):
    cipher = get_cipher(key)
    try:
        decrypted_text = cipher.decrypt(text.encode())
        return decrypted_text
    except Exception as e:
        print(e)
        print('Wrong key')
        return None

    
@app.route('/api/encrypt', methods=['POST'])
@cross_origin(supports_credentials=True)
def encrypt():
    text = request.json['text']
    password = request.json['password']
    timestamp = request.json['timestamp']
    
    key = generate_key()
    encrypted_text = encrypt_text(text, key)
    
    text_hash = sha256_hex(encrypted_text)
    
    row = Keys(hash=text_hash,
               key=key,
               password=hash_password(password),
               timestamp=timestamp)
    db.session.add(row)
    db.session.commit()
    
    shifted_data = shift_chars(encrypted_text)
    return shifted_data


@app.route('/api/decrypt', methods=['POST'])
@cross_origin(supports_credentials=True)
def decrypt():
    password = request.form.get('password', '')
    f = request.files['file']
    file_shifted_data = f.read().decode()
    file_data = unshift_chars(file_shifted_data)

    text_hash = sha256_hex(file_data)
    row = Keys.query.filter_by(hash=text_hash).first()
    
    if row is None:
        abort(422)
    if row.password and (not password or md5_hex(password) != row.password):
        abort(403)
    
    current_timestamp = get_current_timestamp()
    if current_timestamp < row.timestamp:
        abort(422)
    
    decrypted_text = decrypt_text(file_data, row.key)
    return decrypted_text

@app.route('/')
def hello_world():
    return 'Hello, World!'