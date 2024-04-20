from flask import Flask, request, jsonify, render_template
from flask_bcrypt import Bcrypt
import psycopg2
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from utils import returnMsg

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# DB CREDS from .env
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_password = bcrypt.generate_password_hash(
        data['password']).decode('utf-8')

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (fname, lname, email, dob, hometown, gender, password, is_visitor) VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)",
                       (data['fname'], data['lname'], data['email'], data['dob'], data['hometown'], data['gender'], hashed_password))
        conn.commit()

        return returnMsg(True, 'User created successfully', 201)
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)


@app.route('/visitor_signup', methods=['POST'])
def visitor_signup():
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (is_visitor) VALUES (TRUE)")
        conn.commit()

        user_id = cursor.fetchone()[0]

        token = jwt.encode({'user_id': user_id, 'exp': datetime.utcnow() + timedelta(hours=24)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return returnMsg(True, 'Visitor created successfully', 201, {'token': token})
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[1], password):
            token = jwt.encode({
                'user_id': user[0],
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm='HS256')

            return returnMsg(True, 'Login successful', 200, {'token': token})
        else:
            return returnMsg(False, 'Invalid email or password', 401)
    except psycopg2.Error as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)
    
# add friend (user scope)
@app.route('/add-friend', methods=['POST'])
def add_friend():
    data = request.json
    token = request.headers.get('Authorization')
    if not token:
        return returnMsg(False, 'Missing  token', 401)
    try:
  
        decoded_token = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['user_id']
        friend_id = data['friend_id']
        
        cursor = conn.cursor()
        cursor.execute("INSERT into friends (user_id, friend_id) VALUES(%s, %s)",
                       (user_id,friend_id))
        conn.commit()
        
        return returnMsg(True, 'Friend Added Successfully', 201)
    # not legitimate error
    except (jwt.DecodeError, jwt.ExpiredSignatureError, psycopg2.Error) as e:
        conn.rollback()
        return returnMsg(False, str(e), 400)

@app.route('/list-friends', method=['GET'])
def list_friends():
    token = request.header.get('Authorizaton')
    if not token:
        return returnMsg(False, 'Missing  token', 401)
    
    decoded_token = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
    user_id = decoded_token['user_id']
    
    

# SAMPLE AUTHENTICATED ROUTE
@app.route('/decode', methods=['GET'])
def decode_token():
    token = request.headers.get('Authorization')
    if not token:
        return returnMsg(False, 'Missing token', 401)

    try:
        decoded_token = jwt.decode(
            token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token['user_id']

        return returnMsg(True, 'Decoded successfully', 200, {'user_id': user_id})
    except (jwt.DecodeError, jwt.ExpiredSignatureError):
        return returnMsg(False, 'Invalid token', 401)

if __name__ == '__main__':
    app.run(debug=True)