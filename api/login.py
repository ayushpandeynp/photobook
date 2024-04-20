from flask import request
import psycopg2
import jwt
from datetime import datetime, timedelta
from utils import *
from app import app, conn, bcrypt

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